# Package Manager Test Suite

This test suite provides comprehensive testing for the CodeFusion Studio (CFS) Package Manager functionality, covering CLI operations, VS Code integration, project creation, and authentication.

## Test Plan Overview

The test plan covers 15 main test cases with multiple edge cases:

- **PM-001 to PM-005**: CLI package operations (install, update, remove, list)
- **PM-006 to PM-008**: VS Code Command Palette integration
- **PM-009**: Project creation with automatic package installation
- **PM-010**: Authentication with myAnalog/Cloudsmith
- **PM-011 to PM-015**: Additional functionality (help, concurrency, integrity, offline, dependencies)

## Prerequisites

1. **CodeFusion Studio 1.2.0+** installed
2. **Python 3.8+** 
3. **cfsutil** CLI tool available in PATH
4. **VS Code** with CFS extension (for VS Code tests)
5. Network access to package repositories
6. Valid myAnalog/Cloudsmith credentials (for auth tests)

## Installation

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Verify cfsutil is available:
```bash
cfsutil --version
```

## Running Tests

### Quick Start

Run all tests:
```bash
python run_tests.py --type all
```

Run only CLI tests:
```bash
python run_tests.py --type cli
```

Run quick tests (exclude slow/integration):
```bash
python run_tests.py --quick
```

### Using PyTest Directly

Run all tests with verbose output:
```bash
pytest -v
```

Run specific test categories:
```bash
# CLI tests only
pytest -m cli

# VS Code tests only  
pytest -m vscode

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

Run specific test files:
```bash
pytest test_package_manager_cli.py
pytest test_package_manager_vscode.py
pytest test_project_integration.py
pytest test_authentication.py
```

### Test Options

- `--verbose` or `-v`: Detailed output
- `--coverage` or `-c`: Generate coverage report
- `--markers` or `-m`: Filter by markers
- `--quick`: Run only fast tests

## Test Structure

### Test Files

- `test_package_manager_cli.py`: CLI functionality tests
- `test_package_manager_vscode.py`: VS Code integration tests
- `test_project_integration.py`: Project creation and integration tests
- `test_authentication.py`: Authentication and security tests

### Configuration Files

- `conftest.py`: PyTest fixtures and configuration
- `pytest.ini`: PyTest settings
- `requirements-test.txt`: Test dependencies

### Test Helpers

- `CFSUtilHelper`: CLI command execution helper
- `VSCodeHelper`: VS Code automation helper
- `ProjectHelper`: Project operations helper
- `AuthHelper`: Authentication operations helper

## Test Categories

### CLI Tests (test_package_manager_cli.py)

Tests the `cfsutil pkg` commands:
- Package installation, update, removal
- Package listing
- Help documentation
- Concurrent operations
- Package integrity verification
- Offline functionality
- Dependency resolution

### VS Code Tests (test_package_manager_vscode.py)

Tests VS Code Command Palette integration:
- Package operations via Command Palette
- Extension presence verification
- UI feedback testing
- Workspace integration

### Integration Tests (test_project_integration.py)

Tests project creation and package integration:
- Automatic package installation during project creation
- Project templates
- Dependency management
- Workspace configuration

### Authentication Tests (test_authentication.py)

Tests authentication and security:
- myAnalog/Cloudsmith authentication
- Token-based authentication
- Private package access
- Credential storage security
- Multiple repository support

## Test Data

The tests use configurable test packages defined in `conftest.py`:
- `test-sdk-package`: Sample SDK package
- `test-plugin-package`: Sample plugin package
- `test-toolchain-package`: Sample toolchain package

## Edge Cases Covered

Each test includes comprehensive edge case testing:
- Invalid package names
- Network failures
- Insufficient disk space
- Authentication failures
- Concurrent operations
- Corrupted packages
- Missing dependencies

## Customization

### Test Configuration

Modify `test_config` fixture in `conftest.py`:
```python
@pytest.fixture(scope="session")
def test_config():
    return {
        "cfsutil_path": "cfsutil",  # Path to cfsutil
        "test_packages": {
            "sdk": "your-test-sdk",
            "plugin": "your-test-plugin", 
            "toolchain": "your-test-toolchain"
        },
        "timeout": 30,
        "retry_count": 3
    }
```

### Adding New Tests

1. Create test function following naming convention: `test_pmXXX_description`
2. Use appropriate markers: `@pytest.mark.cli`, `@pytest.mark.vscode`, etc.
3. Include edge case testing
4. Use provided helper fixtures
5. Add cleanup using `cleanup_packages` fixture

## Continuous Integration

For CI/CD integration:

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run tests with JUnit output
pytest --junitxml=test-results.xml --cov=. --cov-report=xml

# Run only fast tests in CI
pytest -m "not slow and not integration"
```

## Troubleshooting

### Common Issues

1. **cfsutil not found**: Ensure CFS is installed and cfsutil is in PATH
2. **VS Code tests fail**: Install VS Code and CFS extension
3. **Authentication tests fail**: Provide valid credentials or skip auth tests
4. **Network timeouts**: Increase timeout in test configuration
5. **Permission errors**: Run with appropriate permissions for package installation

### Skipping Tests

Tests automatically skip when prerequisites are missing:
- VS Code tests skip if VS Code not available
- Auth tests skip if authentication commands not implemented
- Integration tests skip if project templates not available

### Debug Mode

Run with maximum verbosity:
```bash
pytest -vvv --tb=long --capture=no
```

## Contributing

When adding new tests:
1. Follow the existing test structure and naming conventions
2. Include comprehensive edge case testing
3. Use appropriate markers and fixtures
4. Update this README with new test descriptions
5. Ensure tests can run in isolation and are idempotent

## Test Results

Tests generate several output formats:
- Console output with pass/fail status
- HTML coverage report (if `--coverage` used)
- JUnit XML for CI integration
- JSON test report for analysis

The test suite provides comprehensive validation of the Package Manager functionality across all supported interfaces and use cases.