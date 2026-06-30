"""
Test suite for Makkal Kural new features:
1. 234 constituencies API endpoint
2. District Compare functionality
3. SLA Countdown (via issue detail)
4. WhatsApp share (frontend component)
5. Anonymous toggle (via issue creation)
6. Landing page with diverse issues
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestConstituenciesAPI:
    """Test the 234 constituencies endpoint"""
    
    def test_get_all_constituencies(self):
        """Test that /api/constants/constituencies returns all 234 constituencies"""
        response = requests.get(f"{BASE_URL}/api/constants/constituencies")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "constituencies" in data, "Response should have 'constituencies' key"
        assert "by_district" in data, "Response should have 'by_district' key"
        assert "total" in data, "Response should have 'total' key"
        
        # Verify we have 234 constituencies
        assert data["total"] == 234, f"Expected 234 constituencies, got {data['total']}"
        assert len(data["constituencies"]) == 234, f"Expected 234 items in list, got {len(data['constituencies'])}"
        
        # Verify structure of constituency items
        first_constituency = data["constituencies"][0]
        assert "name" in first_constituency, "Constituency should have 'name'"
        assert "district" in first_constituency, "Constituency should have 'district'"
        
        print(f"✓ All 234 constituencies returned successfully")
    
    def test_get_constituencies_by_district(self):
        """Test filtering constituencies by district"""
        response = requests.get(f"{BASE_URL}/api/constants/constituencies?district=Chennai")
        assert response.status_code == 200
        
        data = response.json()
        assert "district" in data, "Response should have 'district' key"
        assert data["district"] == "Chennai"
        assert "constituencies" in data
        assert "count" in data
        
        # Chennai should have multiple constituencies
        assert data["count"] > 0, "Chennai should have constituencies"
        assert len(data["constituencies"]) == data["count"]
        
        # All returned should be strings (constituency names)
        for const in data["constituencies"]:
            assert isinstance(const, str), f"Constituency name should be string, got {type(const)}"
        
        print(f"✓ Chennai has {data['count']} constituencies")
    
    def test_constituencies_by_invalid_district(self):
        """Test filtering by non-existent district returns empty"""
        response = requests.get(f"{BASE_URL}/api/constants/constituencies?district=InvalidDistrict")
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 0, "Invalid district should return 0 constituencies"
        assert len(data["constituencies"]) == 0
        
        print("✓ Invalid district returns empty list correctly")


class TestDistrictDashboard:
    """Test district dashboard for compare functionality"""
    
    def test_get_district_dashboard_chennai(self):
        """Test getting Chennai district dashboard"""
        response = requests.get(f"{BASE_URL}/api/dashboard/district/Chennai")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["district"] == "Chennai"
        assert "stats" in data
        
        stats = data["stats"]
        assert "total" in stats
        assert "pending" in stats
        assert "resolved" in stats
        assert "resolution_rate" in stats
        
        print(f"✓ Chennai dashboard: {stats['total']} total issues, {stats['resolution_rate']}% resolution rate")
    
    def test_get_district_dashboard_coimbatore(self):
        """Test getting Coimbatore district dashboard"""
        response = requests.get(f"{BASE_URL}/api/dashboard/district/Coimbatore")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["district"] == "Coimbatore"
        assert "stats" in data
        
        print(f"✓ Coimbatore dashboard: {data['stats']['total']} total issues")
    
    def test_invalid_district_dashboard(self):
        """Test invalid district returns 400"""
        response = requests.get(f"{BASE_URL}/api/dashboard/district/InvalidDistrict")
        assert response.status_code == 400
        
        print("✓ Invalid district returns 400 correctly")


class TestAuthenticationFlow:
    """Test OTP authentication for issue creation"""
    
    def test_send_otp(self):
        """Test sending OTP"""
        response = requests.post(f"{BASE_URL}/api/auth/send-otp", json={"mobile": "9876543210"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "otp_for_testing" in data, "Should return OTP for testing"
        
        print(f"✓ OTP sent successfully: {data['otp_for_testing']}")
        return data["otp_for_testing"]
    
    def test_verify_otp_and_get_token(self):
        """Test verifying OTP and getting JWT token"""
        # First send OTP
        send_response = requests.post(f"{BASE_URL}/api/auth/send-otp", json={"mobile": "9876543210"})
        otp = send_response.json()["otp_for_testing"]
        
        # Verify OTP
        verify_response = requests.post(f"{BASE_URL}/api/auth/verify-otp", json={
            "mobile": "9876543210",
            "otp": otp
        })
        assert verify_response.status_code == 200
        
        data = verify_response.json()
        assert data["success"] == True
        assert "token" in data
        assert "user" in data
        
        print(f"✓ OTP verified, token received")
        return data["token"]


class TestIssueCreationWithAnonymous:
    """Test issue creation with anonymous toggle"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        send_response = requests.post(f"{BASE_URL}/api/auth/send-otp", json={"mobile": "9876543210"})
        otp = send_response.json()["otp_for_testing"]
        
        verify_response = requests.post(f"{BASE_URL}/api/auth/verify-otp", json={
            "mobile": "9876543210",
            "otp": otp
        })
        return verify_response.json()["token"]
    
    def test_create_issue_anonymous(self, auth_token):
        """Test creating an issue with anonymous flag"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        issue_data = {
            "district": "Chennai",
            "local_body_type": "Corporation",
            "local_body_name": "Chennai Corporation",
            "ward": "Ward 10",
            "street": "Test Street",
            "category": "corruption",
            "problem_id": "bribery",
            "description": "TEST_ANONYMOUS: Testing anonymous issue creation for sensitive corruption report",
            "frequency": "daily",
            "affected_people": "10-50",
            "duration": "months",
            "media_urls": [],
            "is_anonymous": True
        }
        
        response = requests.post(f"{BASE_URL}/api/issues", json=issue_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "issue" in data
        
        issue = data["issue"]
        assert issue["is_anonymous"] == True, "Issue should be marked as anonymous"
        assert issue["category"] == "corruption"
        
        print(f"✓ Anonymous issue created: {issue['id']}")
        return issue["id"]
    
    def test_create_issue_non_anonymous(self, auth_token):
        """Test creating a regular (non-anonymous) issue"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        issue_data = {
            "district": "Madurai",
            "local_body_type": "Corporation",
            "local_body_name": "Madurai Corporation",
            "category": "water",
            "problem_id": "no_water",
            "description": "TEST_REGULAR: Testing regular issue creation for water problem",
            "frequency": "daily",
            "affected_people": "entire_area",
            "duration": "weeks",
            "media_urls": [],
            "is_anonymous": False
        }
        
        response = requests.post(f"{BASE_URL}/api/issues", json=issue_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        issue = data["issue"]
        assert issue["is_anonymous"] == False, "Issue should not be anonymous"
        
        print(f"✓ Regular issue created: {issue['id']}")
        return issue["id"]


class TestIssueDetailWithSLA:
    """Test issue detail page with SLA countdown data"""
    
    def test_get_issue_detail_has_escalation_history(self):
        """Test that issue detail includes escalation history for SLA countdown"""
        # First get list of issues
        response = requests.get(f"{BASE_URL}/api/issues?limit=1")
        assert response.status_code == 200
        
        issues = response.json()["issues"]
        if len(issues) == 0:
            pytest.skip("No issues available to test")
        
        issue_id = issues[0]["id"]
        
        # Get issue detail
        detail_response = requests.get(f"{BASE_URL}/api/issues/{issue_id}")
        assert detail_response.status_code == 200
        
        data = detail_response.json()
        assert data["success"] == True
        
        issue = data["issue"]
        assert "escalation_history" in issue, "Issue should have escalation_history"
        assert "current_level" in issue, "Issue should have current_level"
        assert "status" in issue
        
        # Verify escalation history structure
        if len(issue["escalation_history"]) > 0:
            first_entry = issue["escalation_history"][0]
            assert "level" in first_entry
            assert "role_en" in first_entry
            assert "role_ta" in first_entry
            assert "reached_at" in first_entry
            assert "sla_deadline" in first_entry
        
        print(f"✓ Issue {issue_id} has escalation history with {len(issue['escalation_history'])} entries")


class TestEscalationHierarchy:
    """Test escalation hierarchy endpoint"""
    
    def test_get_escalation_hierarchy(self):
        """Test getting the 7-level escalation hierarchy"""
        response = requests.get(f"{BASE_URL}/api/constants/escalation-hierarchy")
        assert response.status_code == 200
        
        data = response.json()
        assert "hierarchy" in data
        
        hierarchy = data["hierarchy"]
        assert len(hierarchy) == 7, f"Expected 7 levels, got {len(hierarchy)}"
        
        # Verify structure
        for level in hierarchy:
            assert "level" in level
            assert "role_en" in level
            assert "role_ta" in level
            assert "sla_days" in level
        
        # Verify levels are 1-7
        levels = [h["level"] for h in hierarchy]
        assert levels == [1, 2, 3, 4, 5, 6, 7], "Levels should be 1-7"
        
        print(f"✓ Escalation hierarchy has 7 levels: VAO → BDO → DC → Secretary → Minister → CS → CM")


class TestOverviewDashboard:
    """Test overview dashboard for landing page"""
    
    def test_get_overview_dashboard(self):
        """Test getting overall platform statistics"""
        response = requests.get(f"{BASE_URL}/api/dashboard/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        
        stats = data["stats"]
        assert "total_issues" in stats
        assert "total_users" in stats
        assert "total_votes" in stats
        
        assert "status_breakdown" in data
        assert "top_districts" in data
        
        print(f"✓ Overview: {stats['total_issues']} issues, {stats['total_users']} users, {stats['total_votes']} votes")


class TestIssuesListWithDiversity:
    """Test issues list for landing page diversity"""
    
    def test_get_issues_list(self):
        """Test getting issues list"""
        response = requests.get(f"{BASE_URL}/api/issues?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "issues" in data
        assert "total" in data
        
        print(f"✓ Issues list: {data['total']} total issues")
    
    def test_filter_issues_by_district(self):
        """Test filtering issues by district"""
        response = requests.get(f"{BASE_URL}/api/issues?district=Chennai&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        for issue in data["issues"]:
            assert issue["district"] == "Chennai", "All issues should be from Chennai"
        
        print(f"✓ District filter works: {len(data['issues'])} Chennai issues")
    
    def test_filter_issues_by_category(self):
        """Test filtering issues by category"""
        response = requests.get(f"{BASE_URL}/api/issues?category=water&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        for issue in data["issues"]:
            assert issue["category"] == "water", "All issues should be water category"
        
        print(f"✓ Category filter works: {len(data['issues'])} water issues")


class TestCategories:
    """Test issue categories endpoint"""
    
    def test_get_categories(self):
        """Test getting all issue categories"""
        response = requests.get(f"{BASE_URL}/api/constants/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        
        categories = data["categories"]
        assert len(categories) >= 10, f"Expected at least 10 categories, got {len(categories)}"
        
        # Verify structure
        for key, cat in categories.items():
            assert "name_en" in cat
            assert "name_ta" in cat
            assert "problems" in cat
            assert len(cat["problems"]) > 0
        
        print(f"✓ {len(categories)} categories available")


class TestDistricts:
    """Test districts endpoint"""
    
    def test_get_districts(self):
        """Test getting all 38 Tamil Nadu districts"""
        response = requests.get(f"{BASE_URL}/api/constants/districts")
        assert response.status_code == 200
        
        data = response.json()
        assert "districts" in data
        
        districts = data["districts"]
        assert len(districts) == 38, f"Expected 38 districts, got {len(districts)}"
        
        # Verify some key districts
        assert "Chennai" in districts
        assert "Coimbatore" in districts
        assert "Madurai" in districts
        
        print(f"✓ All 38 Tamil Nadu districts available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
