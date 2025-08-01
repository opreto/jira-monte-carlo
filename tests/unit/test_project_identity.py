"""Tests for project identity generation."""

from src.domain.project_identity import (
    extract_project_key_from_csv,
    generate_csv_project_id,
    generate_project_id,
)


class TestGenerateProjectId:
    """Test project ID generation from Jira URL and project key."""

    def test_atlassian_cloud_url(self):
        """Test with typical Atlassian Cloud URL."""
        project_id = generate_project_id("https://mycompany.atlassian.net", "PROJ")
        # Test structure, not exact hash
        assert project_id.startswith("mycompany-PROJ-")
        assert len(project_id.split("-")[-1]) == 6  # 6-char hash

    def test_self_hosted_jira(self):
        """Test with self-hosted Jira URL."""
        project_id = generate_project_id("https://jira.company.com", "TEAM")
        # jira.company.com becomes jirapany after removing .com
        assert project_id.startswith("jirapany-TEAM-")
        assert len(project_id.split("-")[-1]) == 6

    def test_url_normalization(self):
        """Test URL normalization works correctly."""
        # These should all produce the same project ID
        id1 = generate_project_id("https://mycompany.atlassian.net", "PROJ")
        id2 = generate_project_id("HTTPS://mycompany.atlassian.net", "PROJ")
        id3 = generate_project_id("https://mycompany.atlassian.net/", "PROJ")

        assert id1 == id2 == id3

    def test_project_key_normalization(self):
        """Test project key is normalized to uppercase."""
        id1 = generate_project_id("https://example.com", "proj")
        id2 = generate_project_id("https://example.com", "PROJ")

        assert id1 == id2

    def test_filesystem_safety(self):
        """Test that generated IDs are filesystem safe."""
        project_id = generate_project_id("https://example.com:8080/jira", "MY/PROJECT")
        # Should replace problematic characters
        assert "/" not in project_id
        assert ":" not in project_id
        assert "\\" not in project_id


class TestExtractProjectKeyFromCsv:
    """Test project key extraction from CSV filenames."""

    def test_standard_format(self):
        """Test extraction from standard format: PROJ-issues.csv"""
        assert extract_project_key_from_csv("PROJ-issues.csv") == "PROJ"
        assert extract_project_key_from_csv("TEAM-export.csv") == "TEAM"
        assert extract_project_key_from_csv("ABC-data.csv") == "ABC"

    def test_embedded_format(self):
        """Test extraction from embedded format: project-PROJ-export.csv"""
        assert extract_project_key_from_csv("project-PROJ-export.csv") == "PROJ"
        assert extract_project_key_from_csv("jira-TEAM-2024.csv") == "TEAM"

    def test_underscore_format(self):
        """Test extraction with underscores."""
        assert extract_project_key_from_csv("PROJ_2024_data.csv") == "PROJ"
        assert extract_project_key_from_csv("data_TEAM_export.csv") == "TEAM"

    def test_with_path(self):
        """Test extraction works with full paths."""
        assert extract_project_key_from_csv("/path/to/PROJ-issues.csv") == "PROJ"
        # Windows path - backslash might be escaped
        assert extract_project_key_from_csv("C:/data/TEAM-export.csv") == "TEAM"

    def test_no_project_key(self):
        """Test returns None when no project key found."""
        assert extract_project_key_from_csv("issues.csv") is None
        assert extract_project_key_from_csv("export-2024.csv") is None
        assert extract_project_key_from_csv("data.csv") is None

    def test_invalid_project_keys(self):
        """Test filters out invalid project keys."""
        # Too short
        assert extract_project_key_from_csv("A-issues.csv") is None
        # Too long
        assert extract_project_key_from_csv("VERYLONGPROJECTKEY-issues.csv") is None
        # Contains numbers
        assert extract_project_key_from_csv("PROJ123-issues.csv") is None


class TestGenerateCsvProjectId:
    """Test CSV project ID generation."""

    def test_with_explicit_project_key(self):
        """Test generation with explicit project key."""
        project_id = generate_csv_project_id("anyfile.csv", "PROJ")
        # local://csv becomes csv after hostname extraction
        assert project_id.startswith("csv-PROJ-")
        assert len(project_id.split("-")[-1]) == 6

    def test_extract_from_filename(self):
        """Test extraction from filename."""
        project_id = generate_csv_project_id("TEAM-issues.csv")
        assert project_id.startswith("csv-TEAM-")
        assert len(project_id.split("-")[-1]) == 6

    def test_no_project_key(self):
        """Test returns None when no project key available."""
        assert generate_csv_project_id("data.csv") is None

    def test_csv_ids_differ_from_jira(self):
        """Test CSV project IDs are different from Jira IDs."""
        csv_id = generate_csv_project_id("file.csv", "PROJ")
        jira_id = generate_project_id("https://company.atlassian.net", "PROJ")

        # Should be different to maintain separation
        assert csv_id != jira_id

        # But should have similar structure
        assert csv_id.startswith("csv-PROJ-")
        assert jira_id.startswith("company-PROJ-")
