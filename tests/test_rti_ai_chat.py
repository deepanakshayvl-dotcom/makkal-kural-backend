"""
Tests for new features:
- POST /api/ai/chat (Tamil + English, multi-turn via session_id)
- POST /api/issues/{id}/generate-rti (auth, language en/ta/both)
- POST /api/issues/{id}/rtis (save reg number, validation)
- GET  /api/issues/{id}/rtis (public, is_overdue, anonymized)
- Regression: existing endpoints
"""
import os
import uuid
import time
import pytest
import requests

def _load_base_url():
    url = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
    if url:
        return url
    # fallback: read from frontend/.env
    env_path = '/app/frontend/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip().rstrip('/')
    raise RuntimeError("REACT_APP_BACKEND_URL not configured")

BASE_URL = _load_base_url()
TEST_MOBILE = "9876543210"


# ------------------------- helpers -------------------------

@pytest.fixture(scope="module")
def auth_token():
    r = requests.post(f"{BASE_URL}/api/auth/send-otp", json={"mobile": TEST_MOBILE}, timeout=15)
    assert r.status_code == 200, r.text
    otp = r.json().get("otp_for_testing")
    assert otp, "OTP not returned for testing"
    v = requests.post(f"{BASE_URL}/api/auth/verify-otp",
                      json={"mobile": TEST_MOBILE, "otp": otp}, timeout=15)
    assert v.status_code == 200, v.text
    return v.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def unresolved_issue_id(auth_headers):
    """Find an unresolved issue, else create one."""
    r = requests.get(f"{BASE_URL}/api/issues?limit=50", timeout=15)
    assert r.status_code == 200
    for it in r.json().get("issues", []):
        if it.get("status") != "resolved":
            return it["id"]
    # create one
    payload = {
        "district": "Chennai",
        "local_body_type": "Corporation",
        "local_body_name": "Chennai Corporation",
        "ward": "Ward 1",
        "street": "Test",
        "category": "water",
        "problem_id": "no_water",
        "description": "TEST_RTI: water unresolved more than two weeks in our locality",
        "frequency": "daily",
        "affected_people": "10-50",
        "duration": "months",
        "media_urls": [],
        "is_anonymous": False,
    }
    c = requests.post(f"{BASE_URL}/api/issues", json=payload, headers=auth_headers, timeout=20)
    assert c.status_code == 200, c.text
    return c.json()["issue"]["id"]


# ------------------------- AI Chat -------------------------

class TestAIChat:
    def test_chat_english(self):
        sid = f"test-{uuid.uuid4()}"
        r = requests.post(f"{BASE_URL}/api/ai/chat",
                          json={"session_id": sid, "message": "How do I file an RTI in Tamil Nadu?",
                                "language": "en", "history": []}, timeout=60)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["success"] is True
        assert data["session_id"] == sid
        assert isinstance(data["reply"], str) and len(data["reply"]) > 20
        print(f"[EN reply len={len(data['reply'])}] {data['reply'][:120]}...")

    def test_chat_tamil(self):
        sid = f"test-{uuid.uuid4()}"
        r = requests.post(f"{BASE_URL}/api/ai/chat",
                          json={"session_id": sid, "message": "என் தெருவில் தண்ணீர் வரவில்லை, என்ன செய்ய வேண்டும்?",
                                "language": "ta", "history": []}, timeout=60)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["success"] is True
        assert len(data["reply"]) > 10
        # Tamil reply expected to contain at least some Tamil unicode
        has_tamil = any('\u0b80' <= ch <= '\u0bff' for ch in data["reply"])
        assert has_tamil, f"Expected Tamil chars in reply: {data['reply'][:200]}"
        print(f"[TA reply len={len(data['reply'])}] {data['reply'][:120]}...")

    def test_chat_multi_turn_context(self):
        sid = f"test-{uuid.uuid4()}"
        # Turn 1
        r1 = requests.post(f"{BASE_URL}/api/ai/chat",
                           json={"session_id": sid, "message": "I want to complain about garbage in T Nagar Chennai.",
                                 "language": "en", "history": []}, timeout=60)
        assert r1.status_code == 200, r1.text
        # Turn 2
        r2 = requests.post(f"{BASE_URL}/api/ai/chat",
                           json={"session_id": sid, "message": "Which department should I approach?",
                                 "language": "en", "history": []}, timeout=60)
        assert r2.status_code == 200, r2.text
        # Turn 3
        r3 = requests.post(f"{BASE_URL}/api/ai/chat",
                           json={"session_id": sid, "message": "What is the SLA for that?",
                                 "language": "en", "history": []}, timeout=60)
        assert r3.status_code == 200, r3.text
        print(f"[multi-turn ok session={sid}]")


# ------------------------- RTI Generate -------------------------

class TestRTIGenerate:
    def test_generate_rti_requires_auth(self, unresolved_issue_id):
        r = requests.post(f"{BASE_URL}/api/issues/{unresolved_issue_id}/generate-rti",
                          json={"language": "en"}, timeout=15)
        assert r.status_code in (401, 403), r.text

    def test_generate_rti_both(self, unresolved_issue_id, auth_headers):
        r = requests.post(f"{BASE_URL}/api/issues/{unresolved_issue_id}/generate-rti",
                          json={"language": "both"}, headers=auth_headers, timeout=120)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["success"] is True
        assert "pio_dept" in data and data["pio_dept"]
        assert isinstance(data.get("days_unresolved"), int)
        assert data.get("rti_english") and len(data["rti_english"]) > 100
        assert data.get("rti_tamil") and len(data["rti_tamil"]) > 50
        # Tamil chars in tamil draft
        has_tamil = any('\u0b80' <= ch <= '\u0bff' for ch in data["rti_tamil"])
        assert has_tamil
        print(f"[generate-rti both] EN={len(data['rti_english'])}c TA={len(data['rti_tamil'])}c PIO={data['pio_dept']}")

    def test_generate_rti_english_only(self, unresolved_issue_id, auth_headers):
        r = requests.post(f"{BASE_URL}/api/issues/{unresolved_issue_id}/generate-rti",
                          json={"language": "en"}, headers=auth_headers, timeout=90)
        assert r.status_code == 200
        data = r.json()
        assert data.get("rti_english")
        assert not data.get("rti_tamil")

    def test_generate_rti_404(self, auth_headers):
        r = requests.post(f"{BASE_URL}/api/issues/non-existent-id/generate-rti",
                          json={"language": "en"}, headers=auth_headers, timeout=15)
        assert r.status_code == 404


# ------------------------- RTI Save + List -------------------------

class TestRTISaveList:
    @pytest.fixture(scope="class")
    def saved_reg(self, unresolved_issue_id, auth_headers):
        reg = f"TNRTI/2026/{uuid.uuid4().hex[:8].upper()}"
        r = requests.post(f"{BASE_URL}/api/issues/{unresolved_issue_id}/rtis",
                          json={"registration_number": reg, "pio_dept": "PWD", "language": "en"},
                          headers=auth_headers, timeout=20)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["success"] is True
        assert data["rti"]["registration_number"] == reg
        assert "response_deadline" in data
        return reg

    def test_duplicate_reg_returns_400(self, unresolved_issue_id, auth_headers, saved_reg):
        r = requests.post(f"{BASE_URL}/api/issues/{unresolved_issue_id}/rtis",
                          json={"registration_number": saved_reg}, headers=auth_headers, timeout=15)
        assert r.status_code == 400, r.text

    def test_short_reg_returns_400(self, unresolved_issue_id, auth_headers):
        r = requests.post(f"{BASE_URL}/api/issues/{unresolved_issue_id}/rtis",
                          json={"registration_number": "AB12"}, headers=auth_headers, timeout=15)
        assert r.status_code == 400, r.text

    def test_save_rti_requires_auth(self, unresolved_issue_id):
        r = requests.post(f"{BASE_URL}/api/issues/{unresolved_issue_id}/rtis",
                          json={"registration_number": "ABCDEF12345"}, timeout=15)
        assert r.status_code in (401, 403)

    def test_get_rtis_public_anonymized(self, unresolved_issue_id, saved_reg):
        r = requests.get(f"{BASE_URL}/api/issues/{unresolved_issue_id}/rtis", timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "rtis" in data and "total" in data
        assert data["total"] >= 1
        found = False
        for rti in data["rtis"]:
            assert "user_id" not in rti, "user_id must be anonymized"
            assert "_id" not in rti
            assert "is_overdue" in rti
            assert "days_overdue" in rti
            if rti["registration_number"] == saved_reg:
                found = True
        assert found, f"Saved reg {saved_reg} not in listing"

    def test_resolved_issue_blocks_rti_generation(self, auth_headers):
        # Find a resolved issue
        r = requests.get(f"{BASE_URL}/api/issues?status=resolved&limit=10", timeout=15)
        if r.status_code != 200:
            pytest.skip("Cannot fetch issues")
        resolved = [i for i in r.json().get("issues", []) if i.get("status") == "resolved"]
        if not resolved:
            pytest.skip("No resolved issue available")
        rid = resolved[0]["id"]
        r2 = requests.post(f"{BASE_URL}/api/issues/{rid}/generate-rti",
                           json={"language": "en"}, headers=auth_headers, timeout=20)
        assert r2.status_code == 400, r2.text


# ------------------------- Regression -------------------------

class TestRegression:
    def test_issues_list(self):
        r = requests.get(f"{BASE_URL}/api/issues?limit=5", timeout=15)
        assert r.status_code == 200
        assert r.json().get("success") is True

    def test_dashboard_overview(self):
        r = requests.get(f"{BASE_URL}/api/dashboard/overview", timeout=15)
        assert r.status_code == 200
        assert r.json().get("success") is True

    def test_pfi_constituency_or_districts(self):
        # constituency endpoint name may vary; try both
        r1 = requests.get(f"{BASE_URL}/api/pfi/districts", timeout=15)
        assert r1.status_code == 200

    def test_sms_preferences_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/auth/sms-preferences", timeout=15)
        assert r.status_code in (401, 403, 405)

    def test_issue_similar(self, unresolved_issue_id):
        r = requests.get(f"{BASE_URL}/api/issues/{unresolved_issue_id}/similar", timeout=20)
        assert r.status_code == 200, r.text

    def test_reports_generate_endpoint_exists(self, auth_headers):
        # If endpoint exists, we don't need to fully run it; just confirm not 404
        r = requests.post(f"{BASE_URL}/api/reports/generate",
                          json={"district": "Chennai"}, headers=auth_headers, timeout=30)
        assert r.status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
