"""Tests for API cache system"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.cache import APICache


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def cache(temp_cache_dir):
    """Create an APICache instance with temporary directory"""
    return APICache(cache_dir=temp_cache_dir, ttl_hours=1.0)


class TestAPICache:
    """Test cases for APICache"""

    def test_initialization(self, temp_cache_dir):
        """Test cache initialization"""
        cache = APICache(cache_dir=temp_cache_dir, ttl_hours=2.0)

        assert cache.cache_dir == temp_cache_dir
        assert cache.ttl == timedelta(hours=2.0)
        assert temp_cache_dir.exists()

    def test_cache_dir_creation(self):
        """Test cache directory is created if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "new_cache_dir"
            assert not cache_dir.exists()

            APICache(cache_dir=cache_dir)
            assert cache_dir.exists()

    def test_get_cache_path(self, cache):
        """Test cache path generation"""
        # Simple key
        path1 = cache._get_cache_path("simple_key")
        assert path1.name == "simple_key.cache"

        # Key with special characters
        path2 = cache._get_cache_path("jira://project TEST/issues")
        assert "/" not in path2.name
        assert ":" not in path2.name
        assert " " not in path2.name

    def test_set_and_get(self, cache):
        """Test setting and getting cache values"""
        test_data = {"issues": [1, 2, 3], "metadata": {"count": 3}}

        # Set value
        cache.set("test_key", test_data)

        # Get value
        retrieved = cache.get("test_key")
        assert retrieved == test_data

    def test_get_nonexistent_key(self, cache):
        """Test getting a non-existent key returns None"""
        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_expiration(self, cache):
        """Test cache expiration"""
        # Set a value
        cache.set("expire_test", "test_value")

        # Mock current time to be after expiration
        future_time = datetime.now() + timedelta(hours=2)
        with patch("src.infrastructure.cache.datetime") as mock_datetime:
            mock_datetime.now.return_value = future_time
            mock_datetime.fromisoformat = datetime.fromisoformat

            result = cache.get("expire_test")
            assert result is None

            # Verify expired cache file was deleted
            cache_path = cache._get_cache_path("expire_test")
            assert not cache_path.exists()

    def test_cache_not_expired(self, cache):
        """Test cache within TTL is returned"""
        # Set a value
        cache.set("ttl_test", "test_value")

        # Mock current time to be within TTL
        future_time = datetime.now() + timedelta(minutes=30)
        with patch("src.infrastructure.cache.datetime") as mock_datetime:
            mock_datetime.now.return_value = future_time
            mock_datetime.fromisoformat = datetime.fromisoformat

            result = cache.get("ttl_test")
            assert result == "test_value"

    def test_corrupted_cache_handling(self, cache):
        """Test handling of corrupted cache files"""
        cache_path = cache._get_cache_path("corrupted")

        # Write corrupted data
        with open(cache_path, "wb") as f:
            f.write(b"corrupted data")

        # Should return None and delete corrupted file
        result = cache.get("corrupted")
        assert result is None
        assert not cache_path.exists()

    def test_clear_specific_key(self, cache):
        """Test clearing a specific cache key"""
        # Set multiple values
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Clear specific key
        cache.clear("key1")

        # Verify key1 is gone but key2 remains
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_clear_all_cache(self, cache):
        """Test clearing all cache"""
        # Set multiple values
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Clear all
        cache.clear()

        # Verify all keys are gone
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

        # Verify cache directory is empty
        cache_files = list(cache.cache_dir.glob("*.cache"))
        assert len(cache_files) == 0

    def test_get_info(self, cache):
        """Test getting cache information"""
        # Set some test data
        cache.set("test1", {"data": "value1"})
        cache.set("test2", {"data": "value2", "list": [1, 2, 3]})

        info = cache.get_info()

        assert info["cache_dir"] == str(cache.cache_dir)
        assert info["ttl_hours"] == 1.0
        assert info["num_entries"] == 2
        assert info["total_size_mb"] > 0
        assert len(info["entries"]) == 2

        # Check entry details
        for entry in info["entries"]:
            assert "key" in entry
            assert "cached_at" in entry
            assert "age_minutes" in entry
            assert "expired" in entry
            assert "size_kb" in entry
            assert not entry["expired"]  # Should not be expired yet

    def test_get_info_with_expired_entries(self, cache):
        """Test cache info with expired entries"""
        # Set a value
        cache.set("old_entry", "old_value")

        # Mock time to make it expired
        future_time = datetime.now() + timedelta(hours=2)
        with patch("src.infrastructure.cache.datetime") as mock_datetime:
            mock_datetime.now.return_value = future_time
            mock_datetime.fromisoformat = datetime.fromisoformat

            info = cache.get_info()

            assert len(info["entries"]) == 1
            assert info["entries"][0]["expired"] is True

    def test_complex_data_types(self, cache):
        """Test caching complex data types"""
        complex_data = {
            "issues": [
                {"id": 1, "title": "Issue 1", "tags": ["bug", "high"]},
                {"id": 2, "title": "Issue 2", "tags": ["feature"]},
            ],
            "metadata": {
                "total": 2,
                "timestamp": datetime.now().isoformat(),
                "nested": {"level": 2, "data": [1, 2, 3]},
            },
            "numbers": [1.5, 2.7, 3.14159],
            "none_value": None,
        }

        cache.set("complex", complex_data)
        retrieved = cache.get("complex")

        assert retrieved == complex_data
        assert retrieved["metadata"]["nested"]["level"] == 2
        assert retrieved["none_value"] is None

    def test_set_with_write_error(self, cache, caplog):
        """Test error handling when writing cache fails"""
        with patch("builtins.open", side_effect=IOError("Disk full")):
            cache.set("fail_key", "test_value")

        # Check error was logged
        assert "Error writing cache for fail_key" in caplog.text

    def test_get_with_read_error(self, cache, caplog):
        """Test error handling when reading cache fails"""
        # Create a cache file
        cache_path = cache._get_cache_path("read_fail")
        cache_path.touch()

        with patch("builtins.open", side_effect=IOError("Read error")):
            result = cache.get("read_fail")

        assert result is None
        assert "Error reading cache for read_fail" in caplog.text

    def test_default_cache_directory(self):
        """Test default cache directory is created in user home"""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home = Path(tmpdir)
            with patch.object(Path, "home", return_value=mock_home):
                cache = APICache()
                expected_path = mock_home / ".sprint-radar" / "cache"
                assert cache.cache_dir == expected_path
                assert cache.cache_dir.exists()
