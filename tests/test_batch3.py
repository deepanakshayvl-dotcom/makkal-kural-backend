"""
Test suite for Makkal Kural Batch 3 features:
1. /api/issues/{id}/similar - Repeat Issue Detector
2. /api/auth/sms-preferences - SMS Alert Settings
3. /api/reports/generate + /api/reports/{district} - Weekly Reports
4. /api/budget + /api/budget/summary - Budget endpoints
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture(scope="module")
def auth_token():
    r = requests.post(f"{BASE_URL}/api/auth/send-otp", json={"mobile": "9876543210"})
    assert r.status_code == 200, f"send-otp failed: {r.text}"
    otp = r.json()["otp_for_testing"]
    v = requests.post(f"{BASE_URL}/api/auth/verify-otp", json={"mobile": "9876543210", "otp": otp})
    assert v.status_code == 200, f"verify-otp failed: {v.text}"
    return v.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def existing_issue_id():
    r = requests.get(f"{BASE_URL}/api/issues?limit=5")
    assert r.status_code == 200
    issues = r.json().get("issues", [])
    if not issues:
        pytest.skip("No seeded issues available")
    return issues[0]["id"]


# ---------- Repeat Issue Detector ----------
class TestRepeatIssueDetector:
    def test_similar_issues_returns_structure(self, existing_issue_id):
        r = requests.get(f"{BASE_URL}/api/issues/{existing_issue_id}/similar")
        assert r.status_code == 200, r.text
        data = r.json()
        # Expected keys
        for k in ["similar_issues", "is_chronic", "is_recurring", "resolved_count", "unresolved_count"]:
            assert k in data, f"Missing key {k} in response: {data}"
        assert isinstance(data["similar_issues"], list)
        assert isinstance(data["is_chronic"], bool)
        assert isinstance(data["is_recurring"], bool)
        assert isinstance(data["resolved_count"], int)
        assert isinstance(data["unresolved_count"], int)

    def test_similar_issues_invalid_id(self):
        r = requests.get(f"{BASE_URL}/api/issues/nonexistent-id-12345/similar")
        # Either 404 or 200 with empty list — both acceptable, but should not 500
        assert r.status_code in (200, 404), f"Unexpected status: {r.status_code} body={r.text}"


# ---------- SMS Alert Settings ----------
class TestSMSPreferences:
    def test_update_sms_preferences_requires_auth(self):
        r = requests.put(f"{BASE_URL}/api/auth/sms-preferences", json={"enabled": True})
        assert r.status_code in (401, 403), f"Expected 401/403, got {r.status_code}"

    def test_update_sms_preferences_success(self, auth_headers):
        payload = {
            "enabled": True,
            "escalation": True,
            "resolution": True,
            "milestone_100": False,
            "dispute_reopen": True,
            "overdue": False,
            "district_weekly": True,
        }
        r = requests.put(f"{BASE_URL}/api/auth/sms-preferences", json=payload, headers=auth_headers)
        assert r.status_code == 200, r.text
        data = r.json()
        # The endpoint should echo cleaned prefs (either at root or nested under 'preferences')
        prefs = data.get("preferences") or data.get("sms_preferences") or data
        for k, v in payload.items():
            assert prefs.get(k) == v, f"Pref {k} not saved correctly: got {prefs.get(k)} expected {v}"

    def test_update_sms_preferences_partial(self, auth_headers):
        payload = {"enabled": False, "escalation": False}
        r = requests.put(f"{BASE_URL}/api/auth/sms-preferences", json=payload, headers=auth_headers)
        assert r.status_code == 200, r.text


# ---------- Weekly Reports ----------
class TestWeeklyReports:
    def test_get_reports_for_district(self):
        r = requests.get(f"{BASE_URL}/api/reports/Chennai")
        assert r.status_code == 200, r.text
        data = r.json()
        assert "reports" in data or isinstance(data, list), f"Unexpected shape: {data}"

    def test_generate_report_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/reports/generate", json={"district": "Chennai"})
        assert r.status_code in (401, 403)

    def test_generate_report_success_or_rate_limited(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/reports/generate",
            json={"district": "Chennai"},
            headers=auth_headers,
            timeout=90,
        )
        # 200 on success OR 429 if already generated today (rate-limited)
        assert r.status_code in (200, 429), f"Got {r.status_code}: {r.text}"
        data = r.json()
        if r.status_code == 200:
            # Should have summary_en + summary_ta + stats somewhere
            report = data.get("report") or data
            text_blob = str(report).lower()
            assert "summary" in text_blob or "stats" in text_blob, f"Report missing summary/stats: {data}"


# ---------- Budget ----------
class TestBudget:
    def test_get_budget_list(self):
        r = requests.get(f"{BASE_URL}/api/budget?district=Chennai&year=2024")
        assert r.status_code == 200, r.text
        data = r.json()
        # Accept list or {budgets: [...]}
        budgets = data.get("budgets") if isinstance(data, dict) else data
        assert isinstance(budgets, list), f"Expected list, got: {data}"

    def test_get_budget_summary(self):
        r = requests.get(f"{BASE_URL}/api/budget/summary?year=2024")
        assert r.status_code == 200, r.text
        data = r.json()
        assert isinstance(data, dict), f"Expected dict, got: {data}"


# ---------- Regression: existing flows still work ----------
class TestRegression:
    def test_issues_list_works(self):
        r = requests.get(f"{BASE_URL}/api/issues?limit=5")
        assert r.status_code == 200
        assert r.json().get("success") is True

    def test_dashboard_overview_works(self):
        r = requests.get(f"{BASE_URL}/api/dashboard/overview")
        assert r.status_code == 200

    def test_districts_works(self):
        r = requests.get(f"{BASE_URL}/api/constants/districts")
        assert r.status_code == 200
        assert len(r.json()["districts"]) == 38


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
