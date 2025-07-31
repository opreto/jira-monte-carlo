"""CLI module for Sprint Radar"""

import os
import sys

# Check if we should use the refactored CLI
USE_REFACTORED_CLI = os.getenv("USE_REFACTORED_CLI", "false").lower() == "true"

# Since there's a naming conflict between cli.py and cli/ directory,
# we need to be careful about imports to avoid circular dependencies
def _get_main():
    """Get the appropriate main function based on configuration"""
    if USE_REFACTORED_CLI:
        # Import from the refactored CLI
        from src.presentation.cli_refactored import main
        return main
    else:
        # Import from the original CLI
        from src.presentation.cli import main as cli_main
        return cli_main

# Export main function
main = _get_main()

__all__ = ['main']