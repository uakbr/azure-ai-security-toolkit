"""Caching helpers for performance optimisation."""
from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any, Callable


def disk_cache(cache_file: Path) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Simple disk cache decorator for deterministic functions."""
    import threading
    
    _lock = threading.Lock()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
            
            with _lock:
                # Read cache once
                if cache_file.exists():
                    try:
                        data = json.loads(cache_file.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        data = {}
                else:
                    data = {}
                
                # Return cached value if exists
                if key in data:
                    return data[key]
                
                # Compute result outside lock
            
            result = func(*args, **kwargs)
            
            with _lock:
                # Re-read cache in case it was updated
                if cache_file.exists():
                    try:
                        data = json.loads(cache_file.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        data = {}
                else:
                    data = {}
                
                data[key] = result
                try:
                    cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                except OSError:
                    # Ignore write errors - cache is best-effort
                    pass
            return result

        return wrapper

    return decorator
