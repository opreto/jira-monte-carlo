#!/usr/bin/env python3
"""Script to validate all templates - can be used in CI/CD or as a pre-commit hook"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.presentation.template_validator import validate_report_templates, print_validation_report


def main():
    """Run template validation and exit with appropriate code"""
    print("🔍 Validating report templates...")
    
    issues = validate_report_templates()
    print_validation_report(issues)
    
    # Exit with error code if there are errors
    errors = [i for i in issues if i['type'] == 'error']
    if errors:
        print(f"\n❌ Validation failed with {len(errors)} errors")
        sys.exit(1)
    else:
        print("\n✅ Validation passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()