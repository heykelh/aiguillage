"""AIGUILLAGE : assistant de tri des incidents construit avec le harnais de développement IA."""

from .triage import trier
from .version import VERSION_REGLES

__all__ = ["trier", "VERSION_REGLES"]
