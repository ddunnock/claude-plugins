"""Unit tests for database models."""

import pytest
from knowledge_mcp.db.models import (
    Project,
    ProjectStatus,
    STATE_TRANSITIONS,
)


class TestProjectStateMachine:
    """Tests for Project state transitions."""

    def test_state_transitions_defined(self) -> None:
        """All states have transition rules."""
        for status in ProjectStatus:
            assert status in STATE_TRANSITIONS

    def test_planning_can_transition_to_active(self) -> None:
        """Planning projects can become active."""
        project = Project(name="Test", status=ProjectStatus.PLANNING)
        assert project.can_transition_to(ProjectStatus.ACTIVE) is True

    def test_planning_can_transition_to_abandoned(self) -> None:
        """Planning projects can be abandoned."""
        project = Project(name="Test", status=ProjectStatus.PLANNING)
        assert project.can_transition_to(ProjectStatus.ABANDONED) is True

    def test_planning_cannot_transition_to_completed(self) -> None:
        """Planning projects cannot skip to completed."""
        project = Project(name="Test", status=ProjectStatus.PLANNING)
        assert project.can_transition_to(ProjectStatus.COMPLETED) is False

    def test_active_can_transition_to_completed(self) -> None:
        """Active projects can be completed."""
        project = Project(name="Test", status=ProjectStatus.ACTIVE)
        assert project.can_transition_to(ProjectStatus.COMPLETED) is True

    def test_completed_is_terminal(self) -> None:
        """Completed is a terminal state."""
        project = Project(name="Test", status=ProjectStatus.COMPLETED)
        for status in ProjectStatus:
            assert project.can_transition_to(status) is False

    def test_abandoned_is_terminal(self) -> None:
        """Abandoned is a terminal state."""
        project = Project(name="Test", status=ProjectStatus.ABANDONED)
        for status in ProjectStatus:
            assert project.can_transition_to(status) is False

    def test_transition_to_valid_updates_status(self) -> None:
        """Valid transition updates status."""
        project = Project(name="Test", status=ProjectStatus.PLANNING)
        project.transition_to(ProjectStatus.ACTIVE)
        assert project.status == ProjectStatus.ACTIVE

    def test_transition_to_invalid_raises(self) -> None:
        """Invalid transition raises ValueError."""
        project = Project(name="Test", status=ProjectStatus.PLANNING)
        with pytest.raises(ValueError, match="Invalid transition"):
            project.transition_to(ProjectStatus.COMPLETED)
