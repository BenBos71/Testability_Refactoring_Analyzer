"""
Base abstract classes and interfaces for the Testability Refactoring Analyzer.

This module defines the core abstractions that all components must implement,
ensuring consistent interfaces and enabling extensibility.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Violation:
    """Represents a single testability violation."""
    rule_name: str
    description: str
    points_deducted: int
    line_number: int
    function_name: str
    is_red_flag: bool = False


@dataclass
class FunctionScore:
    """Represents testability score for a single function."""
    name: str
    line_number: int
    final_score: int
    violations: List[Violation]
    baseline_score: int = 100


@dataclass
class ClassScore:
    """Represents testability score for a class."""
    name: str
    line_number: int
    constructor_violations: List[Violation]
    method_scores: List[FunctionScore]


@dataclass
class FileScore:
    """Represents testability score for an entire file."""
    file_path: str
    overall_score: int
    classification: str
    function_scores: List[FunctionScore]
    class_scores: List[ClassScore]
    red_flags: List[Violation]


class TestabilityRule(ABC):
    """Abstract base class for all testability rules."""
    
    @abstractmethod
    def evaluate(self, node: Any, context: Dict[str, Any]) -> List[Violation]:
        """
        Evaluate a node for testability violations.
        
        Args:
            node: AST node to evaluate
            context: Analysis context (imports, globals, etc.)
            
        Returns:
            List of violations found
        """
        pass
    
    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Return the name of this rule."""
        pass
    
    @property
    @abstractmethod
    def penalty_points(self) -> int:
        """Return the penalty points for violations of this rule."""
        pass


class Analyzer(ABC):
    """Abstract base class for the main analyzer."""
    
    @abstractmethod
    def analyze_file(self, file_path: str) -> FileScore:
        """
        Analyze a single Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            FileScore with complete analysis results
        """
        pass
    
    @abstractmethod
    def analyze_directory(self, directory_path: str) -> List[FileScore]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            List of FileScore objects for all Python files
        """
        pass


class Formatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format(self, file_scores: List[FileScore]) -> str:
        """
        Format analysis results for output.
        
        Args:
            file_scores: List of file analysis results
            
        Returns:
            Formatted string output
        """
        pass
