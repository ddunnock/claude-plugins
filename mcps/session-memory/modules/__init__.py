"""Session memory feature modules.

Each module implements an optional feature that can be enabled/disabled via config.
All modules gracefully degrade if their dependencies are not available.
"""

from typing import TYPE_CHECKING

# Lazy imports to avoid loading dependencies when features are disabled
if TYPE_CHECKING:
    from .embeddings import EmbeddingService
    from .entities import EntityExtractor, KnowledgeGraph, Entity, Relation
    from .learning import LearningService, Learning
    from .cloud_sync import CloudSyncService
    from .document_ingest import DocumentIngestor, DocumentChunk

__all__ = [
    "EmbeddingService",
    "EntityExtractor",
    "KnowledgeGraph",
    "Entity",
    "Relation",
    "LearningService",
    "Learning",
    "CloudSyncService",
    "DocumentIngestor",
    "DocumentChunk",
]
