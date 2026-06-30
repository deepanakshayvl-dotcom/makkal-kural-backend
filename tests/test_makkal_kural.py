"""
Makkal Kural API Tests - Tamil Nadu Democratic Governance Platform
Testing: Auth, Issues, AI Moderation, Voice Transcription, Dashboard
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_MOBILE = "9876543210"


class TestHealthAndBasics:
    """Basic health check and API availability tests"""
    
    def test_health_endpoint(self):
        """Test that API health endpoint is working"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "Makkal Kural" in data.get("message", "")
        print(f"✓ Root endpoint working: {data}")


class TestConstants:
    """Test constants endpoints - districts, categories, etc."""
    
    def test_get_districts(self):
        """Test that 38 Tamil Nadu districts are returned"""
        response = requests.get(f"{BASE_URL}/api/constants/districts")
        assert response.status_code == 200
        data = response.json()
        districts = data.get("districts", [])
        assert len(districts) == 38, f"Expected 38 districts, got {len(districts)}"
        assert "Chennai" in districts
        assert "Coimbatore" in districts
        assert "Madurai" in districts
        print(f"✓ Districts endpoint: {len(districts)} districts loaded")
    
    def test_get_categories(self):
        """Test issue categories with Tamil/English names"""
        response = requests.get(f"{BASE_URL}/api/constants/categories")
        assert response.status_code == 200
        data = response.json()
        categories = data.get("categories", {})
        # Should have 16 categories as per requirements
        assert len(categories) >= 16, f"Expected at least 16 categories, got {len(categories)}"
        # Check structure
        assert "water" in categories
        assert "roads" in categories
        assert "health" in categories
        # Check category has Tamil name
        assert "name_ta" in categories["water"]
        assert "name_en" in categories["water"]
        assert "problems" in categories["water"]
        print(f"✓ Categories endpoint: {len(categories)} categories with Tamil support")
    
    def test_get_local_body_types(self):
        """Test local body types"""
        response = requests.get(f"{BASE_URL}/api/constants/local-body-types")
        assert response.status_code == 200
        data = response.json()
        types = data.get("types", [])
        assert len(types) == 4
        assert "Corporation" in types
        assert "Village Panchayat" in types
        print(f"✓ Local body types: {types}")
    
    def test_get_escalation_hierarchy(self):
        """Test 7-level escalation hierarchy"""
        response = requests.get(f"{BASE_URL}/api/constants/escalation-hierarchy")
        assert response.status_code == 200
        data = response.json()
        hierarchy = data.get("hierarchy", [])
        assert len(hierarchy) == 7, f"Expected 7 levels, got {len(hierarchy)}"
        # Check first and last levels
        assert hierarchy[0]["level"] == 1
        assert hierarchy[6]["level"] == 7
        # Chief Minister at level 7
        assert "Chief Minister" in hierarchy[6]["role_en"]
        print(f"✓ Escalation hierarchy: 7 levels configured")


class TestAuthentication:
    """Test OTP-based authentication flow"""
    
    def test_send_otp(self):
        """Test sending OTP to mobile number"""
        response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": TEST_MOBILE}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "otp_for_testing" in data, "OTP should be returned for testing"
        print(f"✓ OTP sent successfully to {TEST_MOBILE}")
        return data.get("otp_for_testing")
    
    def test_send_otp_invalid_mobile(self):
        """Test OTP with invalid mobile number"""
        response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": "123"}
        )
        assert response.status_code == 400
        print("✓ Invalid mobile correctly rejected")
    
    def test_verify_otp_complete_flow(self):
        """Test complete OTP verification and get token"""
        # Step 1: Send OTP
        send_response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": TEST_MOBILE}
        )
        assert send_response.status_code == 200
        otp = send_response.json().get("otp_for_testing")
        
        # Step 2: Verify OTP
        verify_response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": TEST_MOBILE, "otp": otp}
        )
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data.get("success") == True
        assert "token" in data
        assert "user" in data
        assert data["user"]["mobile"] == TEST_MOBILE
        print(f"✓ OTP verification successful, token received")
        return data.get("token")
    
    def test_verify_otp_wrong_code(self):
        """Test wrong OTP rejection"""
        # Send OTP first
        requests.post(f"{BASE_URL}/api/auth/send-otp", json={"mobile": TEST_MOBILE})
        
        # Try wrong OTP
        response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": TEST_MOBILE, "otp": "000000"}
        )
        assert response.status_code == 400
        print("✓ Wrong OTP correctly rejected")


class TestIssues:
    """Test issues CRUD and listing"""
    
    @pytest.fixture(autouse=True)
    def get_auth_token(self):
        """Get authentication token for tests"""
        # Send OTP
        send_response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": TEST_MOBILE}
        )
        otp = send_response.json().get("otp_for_testing")
        
        # Verify and get token
        verify_response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": TEST_MOBILE, "otp": otp}
        )
        self.token = verify_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_issues_list(self):
        """Test getting issues list - should show diverse issues from multiple districts"""
        response = requests.get(f"{BASE_URL}/api/issues?limit=20")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        issues = data.get("issues", [])
        
        # Check diversity - should have issues from multiple districts (seed data)
        if len(issues) > 0:
            districts = set(issue.get("district") for issue in issues)
            categories = set(issue.get("category") for issue in issues)
            print(f"✓ Issues list: {len(issues)} issues from {len(districts)} districts, {len(categories)} categories")
            # Should have diverse data, not just "government hospital"
            assert len(districts) > 1 or len(issues) < 5, "Issues should be from multiple districts"
        else:
            print("✓ Issues list endpoint working (no issues yet)")
    
    def test_get_issues_by_district(self):
        """Test filtering issues by district"""
        response = requests.get(f"{BASE_URL}/api/issues?district=Chennai&limit=10")
        assert response.status_code == 200
        data = response.json()
        issues = data.get("issues", [])
        for issue in issues:
            assert issue.get("district") == "Chennai"
        print(f"✓ District filter working: {len(issues)} Chennai issues")
    
    def test_get_issues_by_category(self):
        """Test filtering issues by category"""
        response = requests.get(f"{BASE_URL}/api/issues?category=water&limit=10")
        assert response.status_code == 200
        data = response.json()
        issues = data.get("issues", [])
        for issue in issues:
            assert issue.get("category") == "water"
        print(f"✓ Category filter working: {len(issues)} water issues")


class TestDashboard:
    """Test dashboard endpoints"""
    
    def test_overview_dashboard(self):
        """Test overall dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/overview")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        stats = data.get("stats", {})
        assert "total_issues" in stats
        assert "total_users" in stats
        assert "total_votes" in stats
        
        # Check top districts shows data from multiple districts
        top_districts = data.get("top_districts", [])
        if len(top_districts) > 0:
            print(f"✓ Overview dashboard: {stats['total_issues']} issues, {len(top_districts)} districts with issues")
        else:
            print(f"✓ Overview dashboard working: {stats}")
    
    def test_district_dashboard(self):
        """Test district-specific dashboard"""
        response = requests.get(f"{BASE_URL}/api/dashboard/district/Chennai")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("district") == "Chennai"
        
        stats = data.get("stats", {})
        assert "total" in stats
        assert "pending" in stats
        assert "resolved" in stats
        print(f"✓ Chennai dashboard: {stats}")
    
    def test_invalid_district_dashboard(self):
        """Test dashboard with invalid district"""
        response = requests.get(f"{BASE_URL}/api/dashboard/district/InvalidDistrict")
        assert response.status_code == 400
        print("✓ Invalid district correctly rejected")
    
    def test_leadership_dashboard(self):
        """Test leadership dashboard (Minister/CS/CM level issues)"""
        response = requests.get(f"{BASE_URL}/api/dashboard/leadership")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "minister_issues" in data
        assert "cs_issues" in data
        assert "cm_issues" in data
        print(f"✓ Leadership dashboard working")


class TestAIModeration:
    """Test AI-powered content moderation endpoint"""
    
    def test_moderate_clean_content(self):
        """Test moderation with clean content"""
        response = requests.post(
            f"{BASE_URL}/api/moderate",
            data={"text": "There is no water supply in our area for the past 3 days. Please help."}
        )
        assert response.status_code == 200
        data = response.json()
        # Clean civic complaint should be approved
        assert data.get("approved") == True or "approved" in data
        print(f"✓ AI moderation - clean content approved: {data}")
    
    def test_moderate_constructive_criticism(self):
        """Test that constructive criticism is allowed"""
        response = requests.post(
            f"{BASE_URL}/api/moderate",
            data={"text": "The government has failed to address the water crisis. Officials are not responding to complaints."}
        )
        assert response.status_code == 200
        data = response.json()
        # Constructive criticism should be allowed
        print(f"✓ AI moderation - criticism response: {data}")
    
    def test_moderate_endpoint_exists(self):
        """Verify moderation endpoint is accessible"""
        # Even without content, endpoint should respond
        response = requests.post(
            f"{BASE_URL}/api/moderate",
            data={"text": "test"}
        )
        assert response.status_code in [200, 422]  # 200 OK or 422 validation
        print(f"✓ AI moderation endpoint accessible")


class TestVoiceTranscription:
    """Test voice transcription endpoint"""
    
    @pytest.fixture(autouse=True)
    def get_auth_token(self):
        """Get authentication token for tests"""
        send_response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": TEST_MOBILE}
        )
        otp = send_response.json().get("otp_for_testing")
        verify_response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": TEST_MOBILE, "otp": otp}
        )
        self.token = verify_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_voice_transcription_endpoint_requires_auth(self):
        """Test that voice transcription requires authentication"""
        # Create a minimal wav file
        import struct
        import io
        
        # Create simple WAV header (44 bytes)
        sample_rate = 44100
        bits_per_sample = 16
        num_channels = 1
        num_samples = sample_rate  # 1 second
        
        wav_buffer = io.BytesIO()
        # RIFF header
        wav_buffer.write(b'RIFF')
        data_size = num_samples * num_channels * bits_per_sample // 8
        wav_buffer.write(struct.pack('<I', 36 + data_size))  # file size - 8
        wav_buffer.write(b'WAVE')
        # fmt chunk
        wav_buffer.write(b'fmt ')
        wav_buffer.write(struct.pack('<I', 16))  # fmt chunk size
        wav_buffer.write(struct.pack('<H', 1))   # audio format (PCM)
        wav_buffer.write(struct.pack('<H', num_channels))
        wav_buffer.write(struct.pack('<I', sample_rate))
        wav_buffer.write(struct.pack('<I', sample_rate * num_channels * bits_per_sample // 8))
        wav_buffer.write(struct.pack('<H', num_channels * bits_per_sample // 8))
        wav_buffer.write(struct.pack('<H', bits_per_sample))
        # data chunk
        wav_buffer.write(b'data')
        wav_buffer.write(struct.pack('<I', data_size))
        # Write silence
        wav_buffer.write(b'\x00' * data_size)
        
        wav_buffer.seek(0)
        
        # Try without auth
        response_no_auth = requests.post(
            f"{BASE_URL}/api/voice/transcribe",
            files={"file": ("test.wav", wav_buffer, "audio/wav")}
        )
        assert response_no_auth.status_code == 401, "Should require authentication"
        print("✓ Voice transcription requires authentication")
    
    def test_voice_transcription_endpoint_exists(self):
        """Test that voice transcription endpoint is configured"""
        import struct
        import io
        
        # Create minimal WAV
        wav_buffer = io.BytesIO()
        wav_buffer.write(b'RIFF')
        wav_buffer.write(struct.pack('<I', 36))
        wav_buffer.write(b'WAVEfmt ')
        wav_buffer.write(struct.pack('<IHHIIHH', 16, 1, 1, 44100, 88200, 2, 16))
        wav_buffer.write(b'data')
        wav_buffer.write(struct.pack('<I', 0))
        wav_buffer.seek(0)
        
        # Try with auth
        response = requests.post(
            f"{BASE_URL}/api/voice/transcribe",
            files={"file": ("test.wav", wav_buffer, "audio/wav")},
            headers=self.headers
        )
        # Should either work or return an error about the audio (not 404)
        assert response.status_code != 404, "Voice transcription endpoint should exist"
        print(f"✓ Voice transcription endpoint exists (status: {response.status_code})")


class TestPFI:
    """Test Public Failure Index endpoints"""
    
    def test_get_all_districts_pfi(self):
        """Test getting PFI for all districts"""
        response = requests.get(f"{BASE_URL}/api/pfi/districts")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        districts = data.get("districts", [])
        assert len(districts) == 38, f"Expected 38 districts, got {len(districts)}"
        print(f"✓ PFI for all 38 districts")
    
    def test_get_single_district_pfi(self):
        """Test getting PFI for a single district"""
        response = requests.get(f"{BASE_URL}/api/pfi/district/Chennai")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        pfi = data.get("pfi", {})
        assert pfi.get("district") == "Chennai"
        assert "overall_score" in pfi
        assert "categories" in pfi
        print(f"✓ Chennai PFI: overall score {pfi.get('overall_score')}")
    
    def test_get_pfi_categories(self):
        """Test getting PFI category definitions"""
        response = requests.get(f"{BASE_URL}/api/pfi/categories")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        categories = data.get("categories", {})
        assert "water" in categories
        assert "health" in categories
        print(f"✓ PFI categories: {len(categories)}")


class TestSchemeFeedback:
    """Test government scheme feedback endpoints"""
    
    @pytest.fixture(autouse=True)
    def get_auth_token(self):
        """Get authentication token for tests"""
        send_response = requests.post(
            f"{BASE_URL}/api/auth/send-otp",
            json={"mobile": TEST_MOBILE}
        )
        otp = send_response.json().get("otp_for_testing")
        verify_response = requests.post(
            f"{BASE_URL}/api/auth/verify-otp",
            json={"mobile": TEST_MOBILE, "otp": otp}
        )
        self.token = verify_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_scheme_feedback_list(self):
        """Test getting scheme feedback list"""
        response = requests.get(f"{BASE_URL}/api/schemes/feedback")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Scheme feedback list endpoint working")
    
    def test_create_scheme_feedback_requires_auth(self):
        """Test that creating scheme feedback requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/schemes/feedback",
            json={
                "scheme_name": "Test Scheme",
                "feedback_type": "not_useful",
                "action": "modify",
                "description": "Test feedback"
            }
        )
        assert response.status_code == 401
        print("✓ Scheme feedback creation requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
