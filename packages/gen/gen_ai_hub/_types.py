"""
Shared type aliases for the gen_ai_hub package.

These aliases decouple the public API from httpx2 implementation types,
so callers do not need to import httpx2 directly for common use cases.
"""

TimeoutTypes = int | float | tuple[float | None, float | None, float | None, float | None]
