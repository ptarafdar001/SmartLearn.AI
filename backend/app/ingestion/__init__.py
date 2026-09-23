"""
Curriculum Ingestion Package for SmartLearn.AI.
Schema-validated, source-grounded multi-modal curriculum ingestion.
"""

from app.ingestion.pipeline import CurriculumIngestionPipeline
from app.ingestion.schemas import CurriculumManifestSchema

__all__ = ["CurriculumIngestionPipeline", "CurriculumManifestSchema"]
