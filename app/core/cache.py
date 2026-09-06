import time
import threading
from typing import Any, Optional

class SimpleTTLCache:
    """Thread-safe in-memory cache with time-to-live expiration."""

    def __init__(self, default_ttl: float = 120.0):
        self.default_ttl = default_ttl
        self._store = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._store:
                val, expires_at = self._store[key]
                if time.time() < expires_at:
                    return val
                del self._store[key]
            return None

    def set(self, key: str, val: Any, ttl: Optional[float] = None) -> None:
        with self._lock:
            duration = ttl if ttl is not None else self.default_ttl
            self._store[key] = (val, time.time() + duration)

    def invalidate(self, *keys: str) -> None:
        with self._lock:
            for k in keys:
                self._store.pop(k, None)

    def invalidate_prefix(self, prefix: str) -> None:
        with self._lock:
            keys_to_delete = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_delete:
                self._store.pop(k, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

cache = SimpleTTLCache(default_ttl=180.0)
