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

try:
    from .speckit_maal import SpecKitMaalPlugin
    __all__.append("SpecKitMaalPlugin")
except ImportError:
    pass

# Session template plugins
try:
    from .code_review import CodeReviewPlugin
    __all__.append("CodeReviewPlugin")
except ImportError:
    pass

try:
    from .bug_investigation import BugInvestigationPlugin
    __all__.append("BugInvestigationPlugin")
except ImportError:
    pass

try:
    from .feature_impl import FeatureImplementationPlugin
    __all__.append("FeatureImplementationPlugin")
except ImportError:
    pass

try:
    from .research import ResearchPlugin
    __all__.append("ResearchPlugin")
except ImportError:
    pass
