# Contributing to SSL Monitor Pro

Thank you for your interest in contributing to SSL Monitor Pro! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### 1. Fork the Repository

1. Go to [GitLab SSL Monitor Pro](https://gitlab.com/root/ssl-monitor-pro)
2. Click the "Fork" button in the top right
3. Clone your fork locally:
   ```bash
   git clone https://gitlab.com/your-username/ssl-monitor-pro.git
   cd ssl-monitor-pro
   ```

### 2. Create a Feature Branch

```bash
git checkout -b feature/amazing-feature
```

**Branch naming conventions:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### 3. Make Your Changes

Follow our coding standards and best practices (see below).

### 4. Test Your Changes

```bash
# Backend tests
cd backend
python -m pytest tests/ -v --cov=app

# Frontend tests (if applicable)
cd frontend-modern
npm test
```

### 5. Commit Your Changes

Use conventional commit messages:

```bash
git commit -m "feat: add Slack notification integration"
git commit -m "fix: resolve SSL check timeout issue"
git commit -m "docs: update API documentation"
```

**Commit message format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code formatting (no logic changes)
- `refactor:` Code restructuring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 6. Push and Create Merge Request

```bash
git push origin feature/amazing-feature
```

Then create a Merge Request on GitLab with:
- Clear title and description
- Link to related issues
- Screenshots (for UI changes)
- Test results

## 📋 Development Guidelines

### Backend (Python/FastAPI)

**Code Style:**
- Follow PEP 8
- Use Black for formatting: `black .`
- Type hints required for all functions
- Docstrings for all public methods

**Example:**
```python
from typing import List, Optional
from pydantic import BaseModel

async def check_ssl_certificate(
    domain: str, 
    port: int = 443
) -> Optional[SSLCertificate]:
    """
    Check SSL certificate for a domain.
    
    Args:
        domain: Domain name to check
        port: Port number (default: 443)
        
    Returns:
        SSLCertificate object or None if check fails
    """
    # Implementation here
    pass
```

**Testing:**
- Write tests for all new features
- Aim for >80% code coverage
- Use pytest fixtures for test data
- Mock external services (APIs, databases)

**Example test:**
```python
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_ssl_check_valid_domain():
    """Test SSL check for valid domain."""
    with patch('ssl_service.SSLChecker.check_domain') as mock_check:
        mock_check.return_value = {
            "status": "healthy",
            "days_until_expiry": 89,
            "issuer": "Let's Encrypt"
        }
        
        result = await check_ssl_certificate("example.com")
        
        assert result["status"] == "healthy"
        assert result["days_until_expiry"] > 0
```

### Frontend (JavaScript/HTML)

**Code Style:**
- Use ESLint configuration provided
- Prettier for formatting
- Use modern JavaScript (ES6+)
- Follow Alpine.js best practices

**Example:**
```javascript
// Use async/await for API calls
async function fetchDomains() {
    try {
        const response = await fetch('/api/v1/domains/');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch domains:', error);
        throw error;
    }
}

// Alpine.js component
function domainManager() {
    return {
        domains: [],
        loading: false,
        
        async loadDomains() {
            this.loading = true;
            try {
                this.domains = await fetchDomains();
            } finally {
                this.loading = false;
            }
        }
    }
}
```

## 🧪 Testing Requirements

### Backend Tests

**Required test coverage:**
- Unit tests for all services
- Integration tests for API endpoints
- Database tests with test fixtures
- Error handling tests

**Test structure:**
```
backend/tests/
├── unit/
│   ├── test_ssl_service.py
│   ├── test_notification_service.py
│   └── test_stripe_manager.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_database.py
└── fixtures/
    ├── test_data.json
    └── mock_responses.py
```

### Frontend Tests

**Required:**
- Unit tests for utility functions
- Component tests for Alpine.js components
- API integration tests

## 📝 Documentation

### Code Documentation

- Add docstrings to all public functions
- Include type hints
- Document complex algorithms
- Add inline comments for non-obvious code

### API Documentation

- Update OpenAPI/Swagger docs
- Add example requests/responses
- Document error codes and messages

### User Documentation

- Update README.md for user-facing changes
- Create/update deployment guides
- Document new configuration options

## 🚀 Pull Request Process

### Before Submitting

1. **Run all tests:**
   ```bash
   # Backend
   cd backend && pytest tests/ -v
   
   # Frontend
   cd frontend-modern && npm test
   ```

2. **Check code quality:**
   ```bash
   # Backend
   black . --check
   flake8 .
   
   # Frontend
   npm run lint
   ```

3. **Update documentation** if needed

4. **Test manually** if it's a UI change

### Merge Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** must pass:
   - Pipeline runs successfully
   - Tests pass
   - Code quality checks pass

2. **Manual review** by maintainers:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Security considerations

3. **Approval** from at least one maintainer

## 🐛 Bug Reports

When reporting bugs, include:

1. **Environment:**
   - OS and version
   - Python version
   - Browser (for frontend issues)

2. **Steps to reproduce:**
   - Clear, numbered steps
   - Expected vs actual behavior

3. **Additional context:**
   - Error messages/logs
   - Screenshots
   - Related issues

**Template:**
```markdown
## Bug Description
Brief description of the bug

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.11.0]
- Browser: [e.g., Chrome 91.0]

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

For feature requests:

1. **Check existing issues** first
2. **Use the feature request template**
3. **Provide clear use cases**
4. **Consider implementation complexity**

## 🔒 Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email: vla.maidaniuk@gmail.com
2. Subject: "Security Issue - SSL Monitor Pro"
3. Include detailed description and steps to reproduce

### Security Guidelines

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP guidelines
- Keep dependencies updated

## 📞 Getting Help

### Questions?

- 💬 **GitLab Discussions**: [GitLab Issues](https://gitlab.com/root/ssl-monitor-pro/-/issues)
- 📧 **Email**: vla.maidaniuk@gmail.com
- 📖 **Documentation**: Check existing docs in repository

### Development Setup Help

See [LOCAL_DEVELOPMENT_SETUP.md](LOCAL_DEVELOPMENT_SETUP.md) for detailed setup instructions.

## 🎉 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to SSL Monitor Pro!** 🚀