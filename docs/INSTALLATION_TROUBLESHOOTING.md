# Installation Troubleshooting Guide

## ModuleNotFoundError: No module named 'src'

If you encounter this error when running `sprint-radar`:

```
Traceback (most recent call last):
  File ".../sprint-radar", line 4, in <module>
    from src.presentation.cli import main
ModuleNotFoundError: No module named 'src'
```

### Solution

The package needs to be installed in development mode. Follow these steps:

1. **Ensure you're in the project root directory:**
   ```bash
   cd ~/projects/opreto/internal/jira-monte-carlo
   ```

2. **Create and activate a virtual environment (if not already done):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```
   
   The `-e` flag installs the package in "editable" mode, which creates a link to the source code rather than copying files.

4. **Verify the installation:**
   ```bash
   which sprint-radar  # Should show path in your virtual environment
   sprint-radar --help  # Should display help message
   ```

### Alternative Installation Methods

If the above doesn't work, try:

1. **Using pip with explicit path:**
   ```bash
   pip install -e /path/to/jira-monte-carlo
   ```

2. **Running directly with Python:**
   ```bash
   python -m src.presentation.cli --help
   ```

3. **Adding project to PYTHONPATH:**
   ```bash
   export PYTHONPATH=/path/to/jira-monte-carlo:$PYTHONPATH
   sprint-radar --help
   ```

### Common Issues

- **Wrong Python version**: Ensure you're using Python 3.9 or higher
- **Virtual environment not activated**: Always activate your virtual environment before running
- **Old installation artifacts**: Try `pip uninstall sprint-radar` then reinstall
- **Permission issues**: On some systems, you may need to use `pip install --user -e .`

### Verifying Your Setup

Run this diagnostic command:
```bash
python -c "import sys; print('Python:', sys.version); print('Path:', sys.path[:3]); import src.presentation.cli; print('Import successful')"
```

This should show your Python version, path, and confirm the import works.