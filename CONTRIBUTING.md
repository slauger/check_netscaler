# Contributing to check_netscaler

Thank you for your interest in contributing to check_netscaler! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

- Be respectful and constructive in discussions
- Focus on technical merit and project improvement
- Help others learn and grow
- Keep discussions on-topic and professional

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/check_netscaler.git
   cd check_netscaler
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/slauger/check_netscaler.git
   ```
4. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip for package management
- Git for version control

### Install Development Dependencies

```bash
# Install the package in editable mode with development dependencies
pip install -e ".[dev]"

# Or install individual tools
pip install pytest pytest-cov ruff black mypy
```

### Verify Installation

```bash
# Run tests
pytest

# Check code style
ruff check check_netscaler/ tests/
black --check check_netscaler/ tests/

# Run type checking
mypy check_netscaler/
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-command` - New features
- `fix/issue-123` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/improve-client` - Code refactoring

### Commit Messages

Write clear, concise commit messages:

```
Add NTP synchronization monitoring command

- Implement ntp command with offset, stratum, jitter checks
- Add truechimers validation
- Include comprehensive tests
- Update documentation
```

**Format:**
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description with bullet points if needed
- Reference issues: `Fixes #123` or `Closes #123`

### Development Workflow

1. **Keep your fork updated**:
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

2. **Make your changes** in focused, logical commits

3. **Test your changes** thoroughly:
   ```bash
   pytest tests/
   ```

4. **Check code style**:
   ```bash
   ruff check check_netscaler/ tests/
   black check_netscaler/ tests/
   ```

5. **Update documentation** if needed

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=check_netscaler --cov-report=html

# Run specific test file
pytest tests/test_commands/test_state.py

# Run specific test
pytest tests/test_commands/test_state.py::test_state_lbvserver_all_up
```

### Writing Tests

All new features and bug fixes **must** include tests:

```python
def test_new_feature():
    """Test description of what this validates."""
    # Arrange
    mock_response = {"objecttype": [{"name": "test", "state": "UP"}]}

    # Act
    result = some_function(mock_response)

    # Assert
    assert result.state == STATE_OK
    assert "test" in result.message
```

### Test Requirements

- **Unit tests** for all commands
- **Mock-based** testing (no live NetScaler required)
- **Coverage** should not decrease
- Tests must **pass** on Python 3.8, 3.9, 3.10, 3.11, 3.12

## Code Style

We use automated tools to maintain consistent code style:

### Ruff (Linting)

```bash
# Check for issues
ruff check check_netscaler/ tests/

# Auto-fix issues
ruff check --fix check_netscaler/ tests/
```

**Configuration:** `pyproject.toml`
- Line length: 100 characters
- Rules: pycodestyle, pyflakes, isort, flake8-bugbear

### Black (Formatting)

```bash
# Check formatting
black --check check_netscaler/ tests/

# Auto-format
black check_netscaler/ tests/
```

**Configuration:** `pyproject.toml`
- Line length: 100 characters

### Mypy (Type Checking)

```bash
# Run type checking
mypy check_netscaler/
```

**Note:** Type checking is currently soft-enforced (warnings only)

### Style Guidelines

- Use **type hints** for function signatures
- Write **docstrings** for classes and public methods
- Keep functions **focused** and single-purpose
- Use **descriptive** variable names
- Add **comments** for complex logic
- Follow **PEP 8** conventions

## Submitting Changes

### Before Submitting

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black check_netscaler/ tests/`
- [ ] No linting errors: `ruff check check_netscaler/ tests/`
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with upstream

### Pull Request Process

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Reference related issues
   - Describe what changed and why
   - Include testing details

3. **Pull Request Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Related Issues
   Fixes #123

   ## Changes Made
   - Added X feature
   - Fixed Y bug
   - Updated Z documentation

   ## Testing
   - [ ] All existing tests pass
   - [ ] New tests added for new functionality
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] Tests added/updated
   - [ ] No breaking changes (or documented)
   ```

4. **Address review feedback** promptly

5. **Keep PR updated** with upstream changes

### Review Process

- Maintainers will review your PR
- Address feedback and questions
- Make requested changes in new commits
- Once approved, your PR will be merged

## Reporting Bugs

### Before Reporting

- Check existing issues to avoid duplicates
- Test with the latest version
- Gather all relevant information

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command: `check_netscaler ...`
2. Expected: ...
3. Actual: ...

**Environment**
- check_netscaler version: 2.0.x
- Python version: 3.x.x
- NetScaler version: 13.x
- OS: Linux/Windows/macOS

**Output**
```
Paste command output here
```

**Additional Context**
Any other relevant information
```

## Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?
What problem does it solve?

**Proposed Solution**
How should this work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Examples, screenshots, references
```

### Feature Guidelines

- Features should align with project goals
- Consider impact on existing functionality
- Provide use cases and examples
- Be open to discussion and alternatives

## Development Tips

### Testing Against NetScaler

Mock testing is preferred, but if you have access to a test NetScaler:

```bash
# Set environment variables
export NETSCALER_HOST=192.168.1.10
export NETSCALER_USER=monitoring
export NETSCALER_PASS=password

# Run manual tests
check_netscaler -C state -o lbvserver
```

### Adding a New Command

1. Create command file in `check_netscaler/commands/`
2. Inherit from `BaseCommand`
3. Implement `execute()` method
4. Register in `check_netscaler/commands/__init__.py`
5. Add CLI arguments in `check_netscaler/cli.py`
6. Write comprehensive tests in `tests/test_commands/`
7. Add usage examples in `docs/commands/`
8. Update documentation

### Debugging

```bash
# Enable debug output
check_netscaler -C debug -o system

# Use pytest debugging
pytest -vv -s tests/test_commands/test_state.py

# Python debugger
import pdb; pdb.set_trace()
```

## Questions?

- Open an [issue](https://github.com/slauger/check_netscaler/issues) for questions
- Check existing documentation in `docs/` and `examples/`
- Review closed issues and PRs for similar questions

## License

By contributing to check_netscaler, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to check_netscaler!
