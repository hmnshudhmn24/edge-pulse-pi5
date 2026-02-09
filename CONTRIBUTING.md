# Contributing to EdgePulse-Pi5

Thank you for your interest in contributing to EdgePulse-Pi5! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (Raspberry Pi model, OS version, Python version)
- Relevant log files

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature has already been requested
- Provide a clear use case
- Explain how it benefits users
- Consider implementation complexity

### Code Contributions

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/edgepulse-pi5.git
   cd edgepulse-pi5
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Test on actual hardware if possible
   python3 main.py --test
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Python
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Example
```python
def calculate_heart_rate(samples: List[int]) -> Optional[float]:
    """
    Calculate heart rate from IR samples
    
    Args:
        samples: List of IR sensor readings
        
    Returns:
        Heart rate in BPM, or None if calculation fails
    """
    # Implementation
    pass
```

## Testing

All contributions should include tests:

```python
def test_heart_rate_calculation():
    """Test heart rate calculation with known values"""
    samples = [100, 150, 200, 150, 100]
    result = calculate_heart_rate(samples)
    assert result is not None
    assert 40 <= result <= 200
```

## Documentation

Update documentation for:
- New features
- Changed behavior
- New configuration options
- API changes

## Commit Messages

Write clear commit messages:
- Use present tense ("Add feature" not "Added feature")
- First line: brief summary (50 chars max)
- Add detailed description if needed
- Reference issues: "Fixes #123"

## Pull Request Process

1. Update README.md with new features
2. Update CHANGELOG.md
3. Ensure all tests pass
4. Request review from maintainers
5. Address review feedback

## Community Guidelines

- Be respectful and constructive
- Help others in discussions
- Share knowledge and experience
- Focus on what's best for the project

## Questions?

Open an issue or discussion if you have questions about contributing.

Thank you for helping improve EdgePulse-Pi5! 🎉
