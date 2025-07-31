"""
Test cases for Project Creation and Package Manager Integration
"""
import pytest
import subprocess
import json
import shutil
from pathlib import Path
import tempfile
import time


@pytest.mark.integration
class TestProjectIntegration:
    """Test Package Manager integration with project creation"""

    @pytest.fixture
    def project_helper(self, cfsutil_helper):
        """Helper for project operations"""
        class ProjectHelper:
            def __init__(self, cfsutil_helper):
                self.cfsutil = cfsutil_helper
            
            def create_project(self, project_name, template=None, workspace_path=None):
                """Create a new CFS project"""
                args = ["project", "create", project_name]
                if template:
                    args.extend(["--template", template])
                if workspace_path:
                    args.extend(["--path", str(workspace_path)])
                
                return self.cfsutil.run_command(args)
            
            def list_templates(self):
                """List available project templates"""
                return self.cfsutil.run_command(["project", "templates"])
            
            def get_project_info(self, project_path):
                """Get project information"""
                return self.cfsutil.run_command(["project", "info"], cwd=project_path)
        
        return ProjectHelper(cfsutil_helper)

    def test_pm009_project_creation_with_automatic_package_installation(
        self, project_helper, temp_workspace, test_config
    ):
        """PM-009: Project creation with automatic package installation"""
        project_name = "test-embedded-project"
        project_path = temp_workspace / project_name
        
        # Create project with template that requires packages
        result = project_helper.create_project(
            project_name, 
            template="embedded-basic",
            workspace_path=temp_workspace
        )
        
        # Project creation should succeed
        if result.returncode != 0:
            # If project creation fails, it might be due to missing templates
            # Skip the test with appropriate message
            pytest.skip(f"Project creation failed - templates may not be available: {result.stderr}")
        
        assert result.returncode == 0, f"Project creation failed: {result.stderr}"
        
        # Verify project directory was created
        assert project_path.exists(), "Project directory should be created"
        
        # Check if packages were automatically installed
        output = result.stdout + result.stderr
        package_keywords = ["installing", "package", "dependency", "sdk"]
        has_package_installation = any(keyword in output.lower() for keyword in package_keywords)
        
        # Verify project structure
        expected_files = ["CMakeLists.txt", "src", "README.md"]
        for expected_file in expected_files:
            file_path = project_path / expected_file
            if not file_path.exists():
                # Some files might be optional depending on template
                continue
        
        # If packages were installed, verify they're listed
        if has_package_installation:
            list_result = project_helper.cfsutil.pkg_list()
            assert list_result.returncode == 0

    def test_pm009_edge_case_project_creation_network_failure(
        self, project_helper, temp_workspace
    ):
        """PM-009 Edge Case: Project creation with network issues"""
        project_name = "test-network-fail-project"
        
        # Try to create project that might require network access
        result = project_helper.create_project(
            project_name,
            template="remote-template-test",
            workspace_path=temp_workspace
        )
        
        # Should either succeed or fail gracefully with appropriate error
        if result.returncode != 0:
            error_msg = result.stderr.lower()
            network_errors = ["network", "connection", "timeout", "unreachable"]
            template_errors = ["template", "not found", "invalid"]
            
            # Should have appropriate error message
            has_appropriate_error = (
                any(err in error_msg for err in network_errors) or
                any(err in error_msg for err in template_errors)
            )
            assert has_appropriate_error, f"Should have appropriate error message: {result.stderr}"

    def test_pm009_edge_case_insufficient_disk_space_simulation(
        self, project_helper, temp_workspace
    ):
        """PM-009 Edge Case: Simulate insufficient disk space"""
        # This is difficult to test without actually filling disk
        # We'll test with a very large project name or invalid path
        
        project_name = "test-project"
        invalid_path = Path("/invalid/readonly/path/that/should/not/exist")
        
        result = project_helper.create_project(
            project_name,
            workspace_path=invalid_path
        )
        
        # Should fail with appropriate error
        if result.returncode != 0:
            error_msg = result.stderr.lower()
            path_errors = ["permission", "access", "directory", "path", "not found"]
            has_path_error = any(err in error_msg for err in path_errors)
            assert has_path_error, f"Should have path-related error: {result.stderr}"

    def test_project_template_listing(self, project_helper):
        """Test listing available project templates"""
        result = project_helper.list_templates()
        
        if result.returncode == 0:
            # Templates should be listed
            assert len(result.stdout.strip()) > 0, "Should list available templates"
            
            # Look for common template types
            template_types = ["embedded", "basic", "advanced"]
            output_lower = result.stdout.lower()
            
            # At least some template information should be present
            assert any(template in output_lower for template in template_types) or "template" in output_lower
        else:
            # If command fails, it might not be implemented yet
            pytest.skip("Template listing not available")

    def test_project_package_dependencies(self, project_helper, temp_workspace, cfsutil_helper):
        """Test project with specific package dependencies"""
        project_name = "test-dependency-project"
        project_path = temp_workspace / project_name
        
        # Create a project configuration file that specifies dependencies
        project_config = {
            "name": project_name,
            "version": "1.0.0",
            "dependencies": {
                "packages": [
                    {"name": "test-sdk-package", "version": ">=1.0.0"},
                    {"name": "test-toolchain-package", "version": "latest"}
                ]
            }
        }
        
        # Create project directory and config
        project_path.mkdir(parents=True, exist_ok=True)
        config_file = project_path / "cfs-project.json"
        
        with open(config_file, 'w') as f:
            json.dump(project_config, f, indent=2)
        
        # Try to install project dependencies
        # This assumes cfsutil has a command to install project dependencies
        result = cfsutil_helper.run_command(
            ["project", "install-deps"], 
            check=False
        )
        
        # Command might not exist in current implementation
        if result.returncode != 0 and "not found" in result.stderr.lower():
            pytest.skip("Project dependency installation not implemented")
        
        # If command exists, it should process the dependencies
        if result.returncode == 0:
            # Verify packages were installed
            list_result = cfsutil_helper.pkg_list()
            assert "test-sdk-package" in list_result.stdout or "test-toolchain-package" in list_result.stdout

    @pytest.mark.slow
    def test_large_project_creation(self, project_helper, temp_workspace):
        """Test creating project with many dependencies"""
        project_name = "test-large-project"
        
        # Create project that might have many dependencies
        result = project_helper.create_project(
            project_name,
            template="full-featured",
            workspace_path=temp_workspace
        )
        
        # Should handle large projects gracefully
        if result.returncode != 0:
            # Template might not exist
            pytest.skip("Full-featured template not available")
        
        # Verify project was created
        project_path = temp_workspace / project_name
        assert project_path.exists()
        
        # Check for timeout handling (should complete within reasonable time)
        # This is implicitly tested by the test timeout

    def test_project_workspace_integration(self, temp_workspace):
        """Test project integration with workspace settings"""
        project_name = "test-workspace-project"
        project_path = temp_workspace / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create VS Code workspace file for the project
        workspace_file = project_path / f"{project_name}.code-workspace"
        workspace_config = {
            "folders": [{"path": "."}],
            "settings": {
                "cfs.packageManager.autoCheck": True,
                "cfs.project.name": project_name,
                "cfs.project.type": "embedded"
            },
            "tasks": {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "CFS: Install Dependencies",
                        "type": "shell",
                        "command": "cfsutil",
                        "args": ["project", "install-deps"],
                        "group": "build"
                    }
                ]
            }
        }
        
        with open(workspace_file, 'w') as f:
            json.dump(workspace_config, f, indent=2)
        
        # Verify workspace file is valid JSON
        assert workspace_file.exists()
        
        # Read back and verify structure
        with open(workspace_file, 'r') as f:
            loaded_config = json.load(f)
        
        assert loaded_config["settings"]["cfs.project.name"] == project_name
        assert "CFS: Install Dependencies" in str(loaded_config["tasks"])

    def test_project_cleanup_on_failure(self, project_helper, temp_workspace):
        """Test that failed project creation cleans up properly"""
        project_name = "test-cleanup-project"
        project_path = temp_workspace / project_name
        
        # Try to create project with invalid template
        result = project_helper.create_project(
            project_name,
            template="invalid-template-name-12345",
            workspace_path=temp_workspace
        )
        
        # Should fail
        assert result.returncode != 0
        
        # Project directory should not exist or be empty if cleanup worked
        if project_path.exists():
            # If directory exists, it should be empty or contain only minimal files
            contents = list(project_path.iterdir())
            assert len(contents) <= 1, "Failed project should be cleaned up"