"""Base plugin interface for session memory plugins."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PluginState:
    """Plugin-specific state that gets persisted in checkpoints."""

    phase: Optional[str] = None
    progress: float = 0.0
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phase": self.phase,
            "progress": self.progress,
            "custom_data": self.custom_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginState":
        """Create from dictionary."""
        return cls(
            phase=data.get("phase"),
            progress=data.get("progress", 0.0),
            custom_data=data.get("custom_data", {})
        )


@dataclass
class ResumptionContext:
    """Context needed to resume a session."""

    summary: str
    next_steps: List[str]
    blocking_items: List[str]
    state: PluginState

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "summary": self.summary,
            "next_steps": self.next_steps,
            "blocking_items": self.blocking_items,
            "state": self.state.to_dict()
        }


class SessionPlugin(ABC):
    """
    Base class for skill-specific session plugins.

    Plugins provide:
    1. Custom state schemas for skill-specific tracking
    2. Progress calculation logic
    3. Resumption context generation
    4. Event processing hooks
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier (e.g., 'speckit', 'spec-refiner')."""
        pass

    @property
    @abstractmethod
    def supported_skills(self) -> List[str]:
        """List of skill names this plugin handles."""
        pass

    @abstractmethod
    def get_state_schema(self) -> Dict[str, Any]:
        """
        Return JSON Schema for plugin-specific state.
        Used for validation and documentation.
        """
        pass

    @abstractmethod
    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        """
        Calculate progress (0.0 to 1.0) based on events and current state.

        Args:
            events: All events in current session
            state: Current plugin state

        Returns:
            Progress value between 0.0 and 1.0
        """
        pass

    @abstractmethod
    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        """
        Generate context needed to resume a session.

        Args:
            events: Events since last checkpoint
            state: Plugin state at checkpoint
            checkpoint: Checkpoint metadata

        Returns:
            ResumptionContext with summary and next steps
        """
        pass

    def create_initial_state(self) -> PluginState:
        """Create initial state for a new session. Override for custom state."""
        return PluginState()

    def on_event(self, event: Dict, state: PluginState) -> PluginState:
        """
        Hook called when events are recorded. Override to update state.

        Args:
            event: The recorded event
            state: Current plugin state

        Returns:
            Updated plugin state
        """
        return state

    def on_checkpoint(self, checkpoint: Dict, state: PluginState) -> Dict:
        """
        Hook called when checkpoint is created. Override to add custom data.

        Args:
            checkpoint: Checkpoint being created
            state: Current plugin state

        Returns:
            Additional data to include in checkpoint
        """
        return {}

    def validate_state(self, state: Dict) -> bool:
        """Validate state against schema. Override for custom validation."""
        return True
