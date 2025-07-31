"""
PyTest configuration and fixtures for Package Manager tests
"""
import pytest
import subprocess
import os
import tempfile
import shutil
from pathlib import Path
import json
import time


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "cfsutil_path": "cfsutil",  # Assume cfsutil is in PATH
        "test_packages": {
            "sdk": "test-sdk-package",
            "plugin": "test-plugin-package", 
            "toolchain": "test-toolchain-package"
        },
        "timeout": 30,  # seconds
        "retry_count": 3
    }


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for tests"""
    temp_dir = tempfile.mkdtemp(prefix="cfs_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_package_registry(temp_workspace):
    """Mock package registry for testing"""
    registry_file = temp_workspace / "package_registry.json"
    registry_data = {
        "packages": {
            "test-sdk-package": {
                "version": "1.0.0",
                "type": "sdk",
                "status": "available"
            },
            "test-plugin-package": {
                "version": "2.1.0", 
                "type": "plugin",
                "status": "available"
            },
            "test-toolchain-package": {
                "version": "3.0.1",
                "type": "toolchain", 
                "status": "available"
            }
        }
    }
    
    with open(registry_file, 'w') as f:
        json.dump(registry_data, f, indent=2)
    
    return registry_file


class CFSUtilHelper:
    """Helper class for cfsutil command execution"""
    
    def __init__(self, cfsutil_path="cfsutil", timeout=30):
        self.cfsutil_path = cfsutil_path
        self.timeout = timeout
    
    def run_command(self, args, check=True, capture_output=True):
        """Execute cfsutil command with given arguments"""
        cmd = [self.cfsutil_path] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout,
                check=check
            )
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Command timed out: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            if check:
                pytest.fail(f"Command failed: {' '.join(cmd)}\nError: {e.stderr}")
            return e
    
    def pkg_install(self, package_name):
        """Install package via CLI"""
        return self.run_command(["pkg", "install", package_name])
    
    def pkg_remove(self, package_name):
        """Remove package via CLI"""
        return self.run_command(["pkg", "remove", package_name])
    
    def pkg_update(self, package_name):
        """Update package via CLI"""
        return self.run_command(["pkg", "update", package_name])
    
    def pkg_list(self):
        """List installed packages"""
        return self.run_command(["pkg", "list"])
    
    def pkg_help(self):
        """Get package manager help"""
        return self.run_command(["pkg", "--help"])


@pytest.fixture
def cfsutil_helper(test_config):
    """CFSUtil helper fixture"""
    return CFSUtilHelper(
        cfsutil_path=test_config["cfsutil_path"],
        timeout=test_config["timeout"]
    )


@pytest.fixture
def cleanup_packages(cfsutil_helper, test_config):
    """Cleanup test packages after test"""
    yield
    # Cleanup after test
    for package_type, package_name in test_config["test_packages"].items():
        try:
            cfsutil_helper.pkg_remove(package_name)
        except:
            pass  # Ignore cleanup errors


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "cli: mark test as CLI-related"
    )
    config.addinivalue_line(
        "markers", "vscode: mark test as VS Code-related"  
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )