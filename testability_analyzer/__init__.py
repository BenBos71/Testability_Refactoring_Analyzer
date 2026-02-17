"""
Testability Refactoring Analyzer

A static analysis tool that evaluates Python code testability using deterministic,
heuristic-based rules and provides actionable refactoring guidance.
"""

__version__ = "1.1.0"
__author__ = "Testability Analyzer Team"

from .analyzer import TestabilityAnalyzer
from .cli import main

__all__ = ["TestabilityAnalyzer", "main"]
