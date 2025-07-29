"""Tests for template validator"""

from src.presentation.template_validator import TemplateValidator


class TestTemplateValidator:
    def test_detects_empty_sections(self):
        """Test detection of potentially empty sections"""
        validator = TemplateValidator()

        # Template with the issue we encountered
        problematic_template = """
        <div class="chart-container">
            <h2>Process Health Score</h2>
            <div id="health-score-gauge"></div>
            
            <!-- This can be empty -->
            <div id="health-score-breakdown"></div>
            
            <div>
                <h3>Score Breakdown & Insights</h3>
                {% for component in process_health_metrics.health_score_breakdown %}
                <div>{{ component.name }}</div>
                {% endfor %}
            </div>
        </div>
        """

        issues = validator.validate_template_string(problematic_template)

        # Should detect the potentially empty section
        warnings = [i for i in issues if i["type"] == "warning"]
        assert len(warnings) >= 1
        assert any("might render empty" in w["message"] for w in warnings)

    def test_detects_unclosed_tags(self):
        """Test detection of unclosed HTML tags"""
        validator = TemplateValidator()

        bad_template = """
        <div>
            <h2>Title</h2>
            <div>
                <p>Content
            </div>
        <!-- missing closing div -->
        """

        issues = validator.validate_template_string(bad_template)
        errors = [i for i in issues if i["type"] == "error"]
        assert len(errors) >= 1
        assert any("Mismatched" in e["message"] for e in errors)

    def test_detects_multiple_blank_lines(self):
        """Test detection of multiple consecutive blank lines"""
        validator = TemplateValidator()

        template_with_blanks = """<div>Content 1</div>




<div>Content 2</div>"""

        issues = validator.validate_template_string(template_with_blanks)
        warnings = [i for i in issues if i["type"] == "warning"]
        # Check for 5 or more consecutive blank lines (more lenient)
        assert any("consecutive blank lines" in w["message"] for w in warnings)

    def test_detects_unmatched_jinja_blocks(self):
        """Test detection of unmatched Jinja2 blocks"""
        validator = TemplateValidator()

        bad_template = """
        {% if condition %}
            <div>Content</div>
        {% if another_condition %}
            <div>More content</div>
        {% endif %}
        <!-- missing endif for first if -->
        """

        issues = validator.validate_template_string(bad_template)
        errors = [i for i in issues if i["type"] == "error"]
        assert len(errors) >= 1

    def test_clean_template_passes(self):
        """Test that a well-formed template passes validation"""
        validator = TemplateValidator()

        good_template = """
        <div class="container">
            <h2>Title</h2>
            {% if items %}
                <ul>
                {% for item in items %}
                    <li>{{ item.name }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>No items found.</p>
            {% endif %}
        </div>
        """

        issues = validator.validate_template_string(good_template)
        errors = [i for i in issues if i["type"] == "error"]
        assert len(errors) == 0


if __name__ == "__main__":
    # Run a quick test
    validator = TemplateValidator()
    test_template = """
    <div>
        <h3>Empty Section</h3>
        {% for item in empty_list %}
        <p>{{ item }}</p>
        {% endfor %}
    </div>
    """

    issues = validator.validate_template_string(test_template, "test")
    if issues:
        print("Found issues:")
        for issue in issues:
            print(f"  - {issue['type']}: {issue['message']}")
