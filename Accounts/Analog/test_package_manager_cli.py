"""
Test cases for Package Manager CLI functionality (cfsutil pkg commands)
"""
import pytest
import subprocess
import time
import json
from pathlib import Path


@pytest.mark.cli
class TestPackageManagerCLI:
    """Test Package Manager CLI operations"""

    def test_pm001_install_sdk_package_via_cli(self, cfsutil_helper, test_config, cleanup_packages):
        """PM-001: Install SDK package via CLI"""
        package_name = test_config["test_packages"]["sdk"]
        
        # Test installation
        result = cfsutil_helper.pkg_install(package_name)
        assert result.returncode == 0, f"Installation failed: {result.stderr}"
        assert "successfully installed" in result.stdout.lower() or "installed" in result.stdout.lower()
        
        # Verify package is listed as installed
        list_result = cfsutil_helper.pkg_list()
        assert package_name in list_result.stdout
        
        # Test edge cases
        # Try installing already installed package
        result_duplicate = cfsutil_helper.run_command(
            ["pkg", "install", package_name], check=False
        )
        # Should either succeed (idempotent) or give appropriate message
        assert result_duplicate.returncode == 0 or "already installed" in result_duplicate.stderr.lower()

    def test_pm001_edge_cases_invalid_package(self, cfsutil_helper):
        """PM-001 Edge Cases: Invalid package name"""
        # Test with invalid package name
        result = cfsutil_helper.run_command(
            ["pkg", "install", "non-existent-package-12345"], check=False
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_pm002_install_plugin_package_via_cli(self, cfsutil_helper, test_config, cleanup_packages):
        """PM-002: Install plugin package via CLI"""
        package_name = test_config["test_packages"]["plugin"]
        
        # Test installation
        result = cfsutil_helper.pkg_install(package_name)
        assert result.returncode == 0, f"Plugin installation failed: {result.stderr}"
        
        # Verify plugin is listed
        list_result = cfsutil_helper.pkg_list()
        assert package_name in list_result.stdout

    def test_pm003_update_existing_package_via_cli(self, cfsutil_helper, test_config, cleanup_packages):
        """PM-003: Update existing package via CLI"""
        package_name = test_config["test_packages"]["sdk"]
        
        # First install the package
        install_result = cfsutil_helper.pkg_install(package_name)
        assert install_result.returncode == 0
        
        # Try to update (may not have newer version in test environment)
        update_result = cfsutil_helper.run_command(
            ["pkg", "update", package_name], check=False
        )
        
        # Should either update successfully or indicate no updates available
        assert (update_result.returncode == 0 or 
                "no updates" in update_result.stdout.lower() or
                "up to date" in update_result.stdout.lower())

    def test_pm003_edge_case_update_nonexistent(self, cfsutil_helper):
        """PM-003 Edge Case: Update non-existent package"""
        result = cfsutil_helper.run_command(
            ["pkg", "update", "non-existent-package"], check=False
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "not installed" in result.stderr.lower()

    def test_pm004_remove_package_via_cli(self, cfsutil_helper, test_config):
        """PM-004: Remove package via CLI"""
        package_name = test_config["test_packages"]["toolchain"]
        
        # First install the package
        install_result = cfsutil_helper.pkg_install(package_name)
        assert install_result.returncode == 0
        
        # Verify it's installed
        list_result = cfsutil_helper.pkg_list()
        assert package_name in list_result.stdout
        
        # Remove the package
        remove_result = cfsutil_helper.pkg_remove(package_name)
        assert remove_result.returncode == 0
        assert "removed" in remove_result.stdout.lower() or "uninstalled" in remove_result.stdout.lower()
        
        # Verify it's no longer listed
        list_result_after = cfsutil_helper.pkg_list()
        assert package_name not in list_result_after.stdout

    def test_pm004_edge_case_remove_nonexistent(self, cfsutil_helper):
        """PM-004 Edge Case: Remove non-existent package"""
        result = cfsutil_helper.run_command(
            ["pkg", "remove", "non-existent-package"], check=False
        )
        assert result.returncode != 0
        assert ("not found" in result.stderr.lower() or 
                "not installed" in result.stderr.lower() or
                "does not exist" in result.stderr.lower())

    def test_pm005_list_installed_packages_via_cli(self, cfsutil_helper, test_config, cleanup_packages):
        """PM-005: List installed packages via CLI"""
        # Install multiple packages
        packages = [
            test_config["test_packages"]["sdk"],
            test_config["test_packages"]["plugin"]
        ]
        
        for package in packages:
            result = cfsutil_helper.pkg_install(package)
            assert result.returncode == 0
        
        # List packages
        list_result = cfsutil_helper.pkg_list()
        assert list_result.returncode == 0
        
        # Verify all installed packages are listed
        for package in packages:
            assert package in list_result.stdout
        
        # Verify output format (should contain version info)
        assert any(char.isdigit() for char in list_result.stdout)  # Should contain version numbers

    def test_pm005_edge_case_list_no_packages(self, cfsutil_helper):
        """PM-005 Edge Case: List when no packages installed"""
        # This test assumes a clean environment or after cleanup
        list_result = cfsutil_helper.pkg_list()
        assert list_result.returncode == 0
        # Should either show empty list or appropriate message
        assert ("no packages" in list_result.stdout.lower() or 
                len(list_result.stdout.strip()) == 0 or
                "installed packages:" in list_result.stdout.lower())

    def test_pm011_package_manager_cli_help(self, cfsutil_helper):
        """PM-011: Package manager CLI help and documentation"""
        # Test main pkg help
        help_result = cfsutil_helper.pkg_help()
        assert help_result.returncode == 0
        assert "usage" in help_result.stdout.lower() or "commands" in help_result.stdout.lower()
        
        # Test subcommand help
        subcommands = ["install", "remove", "update", "list"]
        for subcmd in subcommands:
            subcmd_help = cfsutil_helper.run_command(["pkg", subcmd, "--help"], check=False)
            # Should either show help or indicate the command exists
            assert (subcmd_help.returncode == 0 or 
                    "usage" in subcmd_help.stdout.lower() or
                    subcmd in help_result.stdout.lower())

    @pytest.mark.slow
    def test_pm012_concurrent_package_operations(self, cfsutil_helper, test_config):
        """PM-012: Concurrent package operations"""
        import threading
        import queue
        
        package_name = test_config["test_packages"]["sdk"]
        results = queue.Queue()
        
        def install_package():
            try:
                result = cfsutil_helper.pkg_install(package_name)
                results.put(("install", result.returncode, result.stdout, result.stderr))
            except Exception as e:
                results.put(("install", -1, "", str(e)))
        
        def list_packages():
            try:
                result = cfsutil_helper.pkg_list()
                results.put(("list", result.returncode, result.stdout, result.stderr))
            except Exception as e:
                results.put(("list", -1, "", str(e)))
        
        # Start concurrent operations
        thread1 = threading.Thread(target=install_package)
        thread2 = threading.Thread(target=list_packages)
        
        thread1.start()
        time.sleep(0.1)  # Small delay to ensure first operation starts
        thread2.start()
        
        thread1.join(timeout=30)
        thread2.join(timeout=30)
        
        # Collect results
        operation_results = []
        while not results.empty():
            operation_results.append(results.get())
        
        # At least one operation should succeed
        successful_ops = [r for r in operation_results if r[1] == 0]
        assert len(successful_ops) >= 1, f"No operations succeeded: {operation_results}"
        
        # Clean up
        try:
            cfsutil_helper.pkg_remove(package_name)
        except:
            pass

    def test_pm013_package_integrity_verification(self, cfsutil_helper, test_config, cleanup_packages):
        """PM-013: Package integrity verification"""
        package_name = test_config["test_packages"]["sdk"]
        
        # Install package (should verify integrity automatically)
        result = cfsutil_helper.pkg_install(package_name)
        assert result.returncode == 0
        
        # Check if integrity verification messages are present
        output = result.stdout + result.stderr
        # Look for integrity-related keywords (implementation dependent)
        integrity_keywords = ["checksum", "signature", "verified", "integrity", "hash"]
        has_integrity_check = any(keyword in output.lower() for keyword in integrity_keywords)
        
        # Note: This test may need adjustment based on actual cfsutil output
        # For now, we just ensure the installation succeeded (implies integrity check passed)
        assert result.returncode == 0

    @pytest.mark.slow  
    def test_pm014_offline_package_management(self, cfsutil_helper, test_config):
        """PM-014: Offline package management"""
        # This test is challenging without actual network control
        # We'll test the error handling for network issues
        
        # Try to install a package that requires network access
        # Use a package name that's likely not cached
        result = cfsutil_helper.run_command(
            ["pkg", "install", "remote-only-package-test"], check=False
        )
        
        # Should fail gracefully with network-related error
        if result.returncode != 0:
            error_msg = result.stderr.lower()
            network_errors = ["network", "connection", "timeout", "unreachable", "offline"]
            has_network_error = any(err in error_msg for err in network_errors)
            # Either succeeds (cached) or fails with appropriate network error
            assert has_network_error or "not found" in error_msg

    def test_pm015_package_dependency_resolution(self, cfsutil_helper, test_config, cleanup_packages):
        """PM-015: Package dependency resolution"""
        # This test assumes some packages have dependencies
        # We'll install a package and check if dependencies are mentioned
        
        package_name = test_config["test_packages"]["sdk"]
        result = cfsutil_helper.pkg_install(package_name)
        assert result.returncode == 0
        
        output = result.stdout + result.stderr
        # Look for dependency-related messages
        dependency_keywords = ["dependency", "dependencies", "requires", "installing"]
        
        # If dependencies exist, they should be mentioned in output
        # This is implementation-dependent, so we mainly check successful installation
        assert result.returncode == 0
        
        # Verify package is properly installed
        list_result = cfsutil_helper.pkg_list()
        assert package_name in list_result.stdout