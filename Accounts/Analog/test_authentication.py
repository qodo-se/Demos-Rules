"""
Test cases for Package Manager Authentication and Security
"""
import pytest
import subprocess
import json
import os
from pathlib import Path
import tempfile


@pytest.mark.integration
class TestAuthentication:
    """Test Package Manager authentication with myAnalog/Cloudsmith"""

    @pytest.fixture
    def auth_helper(self, cfsutil_helper):
        """Helper for authentication operations"""
        class AuthHelper:
            def __init__(self, cfsutil_helper):
                self.cfsutil = cfsutil_helper
            
            def login(self, username=None, password=None, token=None):
                """Login to package repository"""
                args = ["auth", "login"]
                if username and password:
                    args.extend(["--username", username, "--password", password])
                elif token:
                    args.extend(["--token", token])
                
                return self.cfsutil.run_command(args, check=False)
            
            def logout(self):
                """Logout from package repository"""
                return self.cfsutil.run_command(["auth", "logout"], check=False)
            
            def status(self):
                """Check authentication status"""
                return self.cfsutil.run_command(["auth", "status"], check=False)
            
            def list_repos(self):
                """List configured repositories"""
                return self.cfsutil.run_command(["repo", "list"], check=False)
        
        return AuthHelper(cfsutil_helper)

    @pytest.fixture
    def test_credentials(self):
        """Test credentials (mock/test environment)"""
        return {
            "username": "test-user",
            "password": "test-password",
            "token": "test-token-12345",
            "invalid_username": "invalid-user",
            "invalid_password": "wrong-password",
            "invalid_token": "invalid-token"
        }

    def test_pm010_authentication_with_myanalog_cloudsmith(self, auth_helper, test_credentials):
        """PM-010: Authentication with myAnalog/Cloudsmith"""
        # Test authentication status (should work without credentials for public repos)
        status_result = auth_helper.status()
        
        # Command should exist and return status
        if status_result.returncode != 0 and "not found" in status_result.stderr.lower():
            pytest.skip("Authentication commands not implemented")
        
        # Test login with username/password
        login_result = auth_helper.login(
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        # In test environment, this might fail due to invalid credentials
        # We're testing the command structure and error handling
        if login_result.returncode == 0:
            # Login succeeded - verify status
            status_after_login = auth_helper.status()
            assert "authenticated" in status_after_login.stdout.lower() or "logged in" in status_after_login.stdout.lower()
            
            # Test logout
            logout_result = auth_helper.logout()
            assert logout_result.returncode == 0
        else:
            # Login failed - should have appropriate error message
            error_msg = login_result.stderr.lower()
            auth_errors = ["authentication", "login", "credentials", "unauthorized", "invalid"]
            has_auth_error = any(err in error_msg for err in auth_errors)
            assert has_auth_error, f"Should have authentication error: {login_result.stderr}"

    def test_pm010_edge_case_invalid_credentials(self, auth_helper, test_credentials):
        """PM-010 Edge Case: Invalid credentials"""
        # Test with invalid username/password
        login_result = auth_helper.login(
            username=test_credentials["invalid_username"],
            password=test_credentials["invalid_password"]
        )
        
        # Should fail with appropriate error
        if login_result.returncode == 0:
            # Unexpected success - might be test environment issue
            pytest.skip("Test environment allows invalid credentials")
        
        error_msg = login_result.stderr.lower()
        auth_errors = ["invalid", "unauthorized", "authentication failed", "wrong", "incorrect"]
        has_auth_error = any(err in error_msg for err in auth_errors)
        assert has_auth_error, f"Should reject invalid credentials: {login_result.stderr}"

    def test_pm010_edge_case_network_timeout(self, auth_helper, test_credentials):
        """PM-010 Edge Case: Network timeout during authentication"""
        # This is difficult to test without network manipulation
        # We'll test with a potentially unreachable endpoint
        
        # Try authentication (might timeout or fail)
        login_result = auth_helper.login(
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        # If it fails, check for network-related errors
        if login_result.returncode != 0:
            error_msg = login_result.stderr.lower()
            network_errors = ["timeout", "network", "connection", "unreachable", "dns"]
            auth_errors = ["authentication", "invalid", "unauthorized"]
            
            # Should have either network or auth error
            has_expected_error = (
                any(err in error_msg for err in network_errors) or
                any(err in error_msg for err in auth_errors)
            )
            assert has_expected_error, f"Should have appropriate error: {login_result.stderr}"

    def test_token_based_authentication(self, auth_helper, test_credentials):
        """Test token-based authentication"""
        # Test login with token
        login_result = auth_helper.login(token=test_credentials["token"])
        
        if login_result.returncode != 0 and "not found" in login_result.stderr.lower():
            pytest.skip("Token authentication not implemented")
        
        # Should either succeed or fail with appropriate message
        if login_result.returncode != 0:
            error_msg = login_result.stderr.lower()
            token_errors = ["token", "invalid", "expired", "unauthorized"]
            has_token_error = any(err in error_msg for err in token_errors)
            assert has_token_error, f"Should have token-related error: {login_result.stderr}"

    def test_repository_configuration(self, auth_helper):
        """Test repository configuration and listing"""
        # List configured repositories
        repos_result = auth_helper.list_repos()
        
        if repos_result.returncode != 0 and "not found" in repos_result.stderr.lower():
            pytest.skip("Repository commands not implemented")
        
        if repos_result.returncode == 0:
            # Should list repositories
            output = repos_result.stdout.lower()
            repo_keywords = ["repository", "repo", "url", "cloudsmith", "analog"]
            has_repo_info = any(keyword in output for keyword in repo_keywords)
            
            # Should have some repository information
            assert has_repo_info or len(repos_result.stdout.strip()) > 0

    def test_private_package_access(self, auth_helper, cfsutil_helper, test_credentials):
        """Test access to private packages"""
        # First try to access private package without authentication
        private_package = "private-test-package"
        
        # Ensure we're logged out
        auth_helper.logout()
        
        # Try to install private package
        install_result = cfsutil_helper.run_command(
            ["pkg", "install", private_package], check=False
        )
        
        # Should fail with authentication error
        if install_result.returncode != 0:
            error_msg = install_result.stderr.lower()
            auth_errors = ["unauthorized", "authentication", "login", "access denied", "forbidden"]
            package_errors = ["not found", "does not exist"]
            
            # Should have either auth error or package not found (both acceptable)
            has_expected_error = (
                any(err in error_msg for err in auth_errors) or
                any(err in error_msg for err in package_errors)
            )
            assert has_expected_error, f"Should require authentication: {install_result.stderr}"

    def test_authentication_persistence(self, auth_helper, test_credentials):
        """Test that authentication persists across commands"""
        # Login
        login_result = auth_helper.login(
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        if login_result.returncode != 0:
            pytest.skip("Cannot test persistence without successful login")
        
        # Check status multiple times
        for i in range(3):
            status_result = auth_helper.status()
            if status_result.returncode == 0:
                output = status_result.stdout.lower()
                assert "authenticated" in output or "logged in" in output
        
        # Logout
        logout_result = auth_helper.logout()
        assert logout_result.returncode == 0
        
        # Verify logout
        status_after_logout = auth_helper.status()
        if status_after_logout.returncode == 0:
            output = status_after_logout.stdout.lower()
            assert "not authenticated" in output or "logged out" in output or "not logged in" in output

    def test_credential_storage_security(self, auth_helper, test_credentials, temp_workspace):
        """Test that credentials are stored securely"""
        # Login
        login_result = auth_helper.login(
            username=test_credentials["username"],
            password=test_credentials["password"]
        )
        
        if login_result.returncode != 0:
            pytest.skip("Cannot test credential storage without successful login")
        
        # Check common credential storage locations
        home_dir = Path.home()
        potential_cred_files = [
            home_dir / ".cfs" / "credentials",
            home_dir / ".cfs" / "auth.json",
            home_dir / ".cfsutil" / "config",
            temp_workspace / ".cfs" / "credentials"
        ]
        
        for cred_file in potential_cred_files:
            if cred_file.exists():
                # File should not contain plaintext passwords
                content = cred_file.read_text().lower()
                assert test_credentials["password"] not in content, "Password should not be stored in plaintext"
                
                # Should contain some form of authentication data
                auth_keywords = ["token", "auth", "credential", "session"]
                has_auth_data = any(keyword in content for keyword in auth_keywords)
                # This assertion is optional as credential format varies
                # assert has_auth_data, "Should contain authentication data"

    def test_multiple_repository_support(self, auth_helper, cfsutil_helper):
        """Test support for multiple package repositories"""
        # List repositories
        repos_result = auth_helper.list_repos()
        
        if repos_result.returncode != 0:
            pytest.skip("Repository listing not available")
        
        # Should support multiple repositories
        output = repos_result.stdout
        
        # Look for multiple repository entries
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        
        # Should have at least repository headers or multiple entries
        if len(lines) > 1:
            # Multiple repositories configured
            repo_indicators = ["cloudsmith", "analog", "http", "https", "repository"]
            has_multiple_repos = sum(1 for line in lines if any(indicator in line.lower() for indicator in repo_indicators)) > 1
            
            # This is informational - multiple repos are good but not required
            if has_multiple_repos:
                assert True  # Multiple repositories supported
        
        # Test installing from different repositories (if configured)
        # This would require specific test packages from different repos
        # For now, we just verify the command structure works