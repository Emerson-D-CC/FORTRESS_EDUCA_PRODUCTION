from __future__ import annotations

import time
import threading
from typing import Any, Callable


class _TTLCache:
    """Dict con expiración automática por entrada."""

    def __init__(self, ttl: float = 45.0) -> None:
        self._store:  dict[str, Any]   = {}
        self._expiry: dict[str, float] = {}
        self._lock = threading.Lock()
        self._ttl  = ttl

    # ------------------------------------------------------------------
    def get_or_set(self, key: str, loader: Callable[[], Any]) -> Any:
        """Devuelve el valor cacheado o lo computa con *loader* y lo guarda."""
        with self._lock:
            now = time.monotonic()
            if key in self._store and now < self._expiry[key]:
                return self._store[key]          # caché hit
            value = loader()                     # caché miss → consulta BD
            self._store[key]  = value
            self._expiry[key] = now + self._ttl
            return value

    # ------------------------------------------------------------------
    def invalidate(self, *keys: str) -> None:
        """Elimina entradas (llamar tras escrituras: toggle, insert…)."""
        with self._lock:
            for k in keys:
                self._store.pop(k, None)
                self._expiry.pop(k, None)

    # ------------------------------------------------------------------
    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self._expiry.clear()


# Instancia global compartida por todos los servicios
sp_cache = _TTLCache(ttl=45)   # 45 s de vida por entrada