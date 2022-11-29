"""Transcript structure generator package."""
import importlib.metadata

from tsg.main import Gtf, TranscriptGenerator, sample_transcripts

__version__ = importlib.metadata.version("tsg")
__all__ = ["Gtf", "TranscriptGenerator", "sample_transcripts"]
