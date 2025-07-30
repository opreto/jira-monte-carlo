"""Simple file-based cache for API responses"""

import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class APICache:
    """
    Simple file-based cache for API responses.

    Stores cached data in the user's home directory under ~/.jira-monte-carlo/cache/
    """

    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: float = 1.0):
        """
        Initialize cache.

        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.jira-monte-carlo/cache/
            ttl_hours: Time to live for cache entries in hours. Default is 1 hour.
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".jira-monte-carlo" / "cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

        logger.info(
            f"Initialized cache at {self.cache_dir} with TTL of {ttl_hours} hours"
        )

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key"""
        # Replace any characters that might cause filesystem issues
        safe_key = key.replace("/", "_").replace(":", "_").replace(" ", "_")
        return self.cache_dir / f"{safe_key}.cache"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if it exists and is not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            logger.debug(f"Cache miss: {key} (file not found)")
            return None

        try:
            with open(cache_path, "rb") as f:
                data = pickle.load(f)

            # Check if expired
            cached_time = datetime.fromisoformat(data["timestamp"])
            if datetime.now() - cached_time > self.ttl:
                logger.info(f"Cache expired: {key} (cached at {cached_time})")
                cache_path.unlink()  # Delete expired cache
                return None

            logger.info(f"Cache hit: {key} (cached at {cached_time})")
            return data["value"]

        except Exception as e:
            logger.error(f"Error reading cache for {key}: {e}")
            # Delete corrupted cache file
            cache_path.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(key)

        data = {"timestamp": datetime.now().isoformat(), "value": value}

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(data, f)
            logger.info(f"Cached: {key}")
        except Exception as e:
            logger.error(f"Error writing cache for {key}: {e}")

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache.

        Args:
            key: Specific key to clear. If None, clears all cache.
        """
        if key:
            cache_path = self._get_cache_path(key)
            cache_path.unlink(missing_ok=True)
            logger.info(f"Cleared cache: {key}")
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            logger.info("Cleared all cache")

    def get_info(self) -> dict:
        """Get information about the cache"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)

        info = {
            "cache_dir": str(self.cache_dir),
            "ttl_hours": self.ttl.total_seconds() / 3600,
            "num_entries": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
            "entries": [],
        }

        for cache_file in cache_files:
            try:
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)

                cached_time = datetime.fromisoformat(data["timestamp"])
                age = datetime.now() - cached_time
                expired = age > self.ttl

                info["entries"].append(
                    {
                        "key": cache_file.stem,
                        "cached_at": data["timestamp"],
                        "age_minutes": int(age.total_seconds() / 60),
                        "expired": expired,
                        "size_kb": cache_file.stat().st_size / 1024,
                    }
                )
            except Exception:
                pass

        return info
