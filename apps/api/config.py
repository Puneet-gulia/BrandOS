"""API-level config. Re-exports shared Settings for convenience."""
from packages.shared.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]
