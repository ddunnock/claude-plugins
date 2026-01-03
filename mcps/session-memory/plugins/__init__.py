"""Session Memory MCP Server Plugins."""

from .base import SessionPlugin, PluginState, ResumptionContext
from .generic import GenericPlugin

__all__ = ["SessionPlugin", "PluginState", "ResumptionContext", "GenericPlugin"]

# Optional skill-specific plugins
try:
    from .speckit import SpecKitPlugin
    __all__.append("SpecKitPlugin")
except ImportError:
    pass

try:
    from .spec_refiner import SpecRefinerPlugin
    __all__.append("SpecRefinerPlugin")
except ImportError:
    pass
