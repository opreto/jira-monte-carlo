"""Template validation utilities for catching common issues"""

import re
from typing import Dict, List

from jinja2 import Environment, TemplateSyntaxError, meta


class TemplateValidator:
    """Validates Jinja2 templates for common issues"""

    def __init__(self):
        self.env = Environment()
        self.issues = []

    def validate_template_string(self, template_str: str, name: str = "template") -> List[Dict[str, any]]:
        """Validate a template string and return list of issues"""
        self.issues = []

        # Check Jinja2 syntax
        self._check_jinja_syntax(template_str, name)

        # Check HTML structure
        self._check_html_structure(template_str, name)

        # Check for common template issues
        self._check_template_patterns(template_str, name)

        return self.issues

    def _check_jinja_syntax(self, template_str: str, name: str):
        """Check for Jinja2 syntax errors"""
        try:
            # Parse the template
            ast = self.env.parse(template_str)

            # Check for undefined variables (basic check)
            undeclared = meta.find_undeclared_variables(ast)
            if undeclared:
                self.issues.append(
                    {
                        "type": "warning",
                        "message": f"Potentially undefined variables: {', '.join(undeclared)}",
                        "template": name,
                    }
                )

        except TemplateSyntaxError as e:
            self.issues.append(
                {
                    "type": "error",
                    "message": f"Jinja2 syntax error: {str(e)}",
                    "line": e.lineno,
                    "template": name,
                }
            )

    def _check_html_structure(self, template_str: str, name: str):
        """Check for HTML structure issues"""
        # Remove Jinja2 tags for HTML analysis
        html_only = re.sub(r"{%.*?%}", "", template_str, flags=re.DOTALL)
        html_only = re.sub(r"{{.*?}}", "", html_only, flags=re.DOTALL)

        # Check for unclosed tags
        tags_to_check = [
            "div",
            "table",
            "tr",
            "td",
            "ul",
            "ol",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "p",
        ]

        for tag in tags_to_check:
            open_tags = len(re.findall(f"<{tag}[^>]*>", html_only, re.IGNORECASE))
            close_tags = len(re.findall(f"</{tag}>", html_only, re.IGNORECASE))

            if open_tags != close_tags:
                self.issues.append(
                    {
                        "type": "error",
                        "message": f"Mismatched {tag} tags: {open_tags} opening, {close_tags} closing",
                        "template": name,
                    }
                )

        # Check for quotes in attributes
        # Look for potential unclosed quotes
        lines = template_str.split("\n")
        for i, line in enumerate(lines):
            # Skip Jinja2 expressions
            if "{%" in line or "{{" in line:
                continue

            # Count quotes in HTML attributes
            if '="' in line:
                quote_count = line.count('"')
                if quote_count % 2 != 0:
                    self.issues.append(
                        {
                            "type": "warning",
                            "message": "Odd number of quotes in line - possible unclosed attribute",
                            "line": i + 1,
                            "template": name,
                            "content": line.strip()[:80],
                        }
                    )

    def _check_template_patterns(self, template_str: str, name: str):
        """Check for common template anti-patterns"""

        # Check for empty sections
        empty_section_pattern = r"{%\s*for\s+\w+\s+in\s+[\w.]+\s*%}\s*{%\s*endfor\s*%}"
        if re.search(empty_section_pattern, template_str):
            self.issues.append(
                {
                    "type": "warning",
                    "message": "Empty for loop detected - consider adding default content",
                    "template": name,
                }
            )

        # Check for sections that might render empty content
        # Pattern: div with conditional content that might all be empty
        potential_empty_sections = re.finditer(
            r"<div[^>]*>\s*<h[23][^>]*>([^<]+)</h[23]>\s*{%\s*for\s+\w+\s+in\s+([\w.]+)\s*%}",
            template_str,
            re.IGNORECASE | re.DOTALL,
        )
        for match in potential_empty_sections:
            section_title = match.group(1).strip()
            collection = match.group(2)
            line_no = template_str[: match.start()].count("\n") + 1
            self.issues.append(
                {
                    "type": "warning",
                    "message": f'Section "{section_title}" might render empty if {collection} is empty',
                    "line": line_no,
                    "template": name,
                }
            )

        # Check for nested conditions that might create empty output
        lines = template_str.split("\n")
        depth = 0
        condition_stack = []

        for i, line in enumerate(lines):
            # Track if/for depth
            if re.search(r"{%\s*if\s+", line) or re.search(r"{%\s*for\s+", line):
                depth += 1
                condition_stack.append((i + 1, line.strip()))
            elif re.search(r"{%\s*endif\s*%}", line) or re.search(r"{%\s*endfor\s*%}", line):
                depth -= 1
                if depth < 0:
                    self.issues.append(
                        {
                            "type": "error",
                            "message": "Unmatched endif/endfor",
                            "line": i + 1,
                            "template": name,
                        }
                    )

        if depth != 0:
            self.issues.append(
                {
                    "type": "error",
                    "message": f"Unclosed if/for blocks: depth={depth}",
                    "template": name,
                }
            )

        # Check for multiple consecutive blank lines (common rendering issue)
        if "\n\n\n\n" in template_str:
            self.issues.append(
                {
                    "type": "warning",
                    "message": "Multiple consecutive blank lines detected - may cause rendering issues",
                    "template": name,
                }
            )

        # Check for potentially hidden content patterns
        # e.g., divs that only render when all conditions are false
        hidden_content_pattern = r"{%\s*if\s+[\w.]+\s*%}[\s\n]*{%\s*endif\s*%}"
        matches = re.finditer(hidden_content_pattern, template_str)
        for match in matches:
            line_no = template_str[: match.start()].count("\n") + 1
            self.issues.append(
                {
                    "type": "warning",
                    "message": "Empty conditional block - content will never be displayed",
                    "line": line_no,
                    "template": name,
                }
            )


def validate_report_templates():
    """Validate all report templates"""
    from .templates import ReportTemplates

    validator = TemplateValidator()
    all_issues = []

    # Get template strings
    templates = {
        "base_template": ReportTemplates.get_base_template(),
        "single_report": ReportTemplates.get_single_report_template(),
        "dashboard": ReportTemplates.get_dashboard_template(),
    }

    for name, template in templates.items():
        # Extract the template string from Jinja2 Template object
        template_str = template.source if hasattr(template, "source") else str(template)
        issues = validator.validate_template_string(template_str, name)
        all_issues.extend(issues)

    return all_issues


def print_validation_report(issues: List[Dict[str, any]]):
    """Print a formatted validation report"""
    if not issues:
        print("✅ All templates validated successfully!")
        return

    errors = [i for i in issues if i["type"] == "error"]
    warnings = [i for i in issues if i["type"] == "warning"]

    print("\n🔍 Template Validation Report")
    print(f"{'=' * 50}")
    print(f"❌ Errors: {len(errors)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    print(f"{'=' * 50}\n")

    if errors:
        print("ERRORS:")
        for issue in errors:
            print(f"  ❌ [{issue['template']}] {issue['message']}")
            if "line" in issue:
                print(f"     Line {issue['line']}")
            if "content" in issue:
                print(f"     > {issue['content']}")
            print()

    if warnings:
        print("\nWARNINGS:")
        for issue in warnings:
            print(f"  ⚠️  [{issue['template']}] {issue['message']}")
            if "line" in issue:
                print(f"     Line {issue['line']}")
            if "content" in issue:
                print(f"     > {issue['content']}")
            print()


if __name__ == "__main__":
    # Run validation when executed directly
    issues = validate_report_templates()
    print_validation_report(issues)
