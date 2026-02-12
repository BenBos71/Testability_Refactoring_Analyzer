"""
Threshold classification system for testability scores.

Provides score band classification and threshold-based recommendations
for both file-level and function-level scores.
"""

from typing import Dict, Any, List
from ..base import FileScore, FunctionScore, Violation


class ThresholdClassifier:
    """Classifies testability scores into bands and provides recommendations."""
    
    def __init__(self):
        # File-level score bands
        self.file_bands = {
            'Healthy': (80, 100),
            'Caution': (60, 79),
            'High Friction': (40, 59),
            'Refactor First': (0, 39)
        }
        
        # Function-level score bands
        self.function_bands = {
            'Easy': (75, 100),
            'Testable': (55, 74),
            'Hard': (35, 54),
            'Painful': (0, 34)
        }
        
        # Red flag rules (always flagged regardless of score)
        self.red_flag_rules = {
            'Constructor Side Effects',
            'Global State Mutation',
            'Non-Deterministic Time Usage',
            'Mixed I/O and Logic',
            'Exception-Driven Control Flow'
        }
    
    def classify_file_score(self, score: int) -> str:
        """
        Classify a file-level score into a band.
        
        Args:
            score: File-level score to classify
            
        Returns:
            Band name as string
        """
        for band_name, (min_score, max_score) in self.file_bands.items():
            if min_score <= score <= max_score:
                return band_name
        
        return 'Unknown'
    
    def classify_function_score(self, score: int) -> str:
        """
        Classify a function-level score into a band.
        
        Args:
            score: Function-level score to classify
            
        Returns:
            Band name as string
        """
        for band_name, (min_score, max_score) in self.function_bands.items():
            if min_score <= score <= max_score:
                return band_name
        
        return 'Unknown'
    
    def get_file_recommendations(self, band: str) -> List[str]:
        """
        Get recommendations for a file-level score band.
        
        Args:
            band: Score band name
            
        Returns:
            List of recommendation strings
        """
        recommendations = {
            'Healthy': [
                "Maintain current testability practices",
                "Consider adding more unit tests for edge cases",
                "Document any complex business logic"
            ],
            'Caution': [
                "Review functions with low scores for refactoring opportunities",
                "Extract complex logic into separate, testable functions",
                "Reduce dependencies on external systems",
                "Add comprehensive unit tests"
            ],
            'High Friction': [
                "Prioritize refactoring of functions with red flags",
                "Break down large functions into smaller, focused ones",
                "Eliminate global state mutations",
                "Separate I/O operations from business logic",
                "Consider dependency injection for better testability"
            ],
            'Refactor First': [
                "Major refactoring required before adding new features",
                "Focus on eliminating structural red flags first",
                "Consider rewriting complex functions from scratch",
                "Implement comprehensive integration tests",
                "Establish testability guidelines for the team"
            ]
        }
        
        return recommendations.get(band, ["No specific recommendations available"])
    
    def get_function_recommendations(self, band: str) -> List[str]:
        """
        Get recommendations for a function-level score band.
        
        Args:
            band: Score band name
            
        Returns:
            List of recommendation strings
        """
        recommendations = {
            'Easy': [
                "Function is well-structured and testable",
                "Add edge case tests if not already present"
            ],
            'Testable': [
                "Consider reducing parameter count if > 5",
                "Extract any remaining complex logic",
                "Add more comprehensive test coverage"
            ],
            'Hard': [
                "Refactor to reduce complexity",
                "Eliminate side effects and global state usage",
                "Separate concerns (I/O vs logic)",
                "Reduce branching complexity"
            ],
            'Painful': [
                "Complete rewrite recommended",
                "Break into multiple smaller functions",
                "Eliminate all non-deterministic behavior",
                "Remove all side effects from business logic"
            ]
        }
        
        return recommendations.get(band, ["No specific recommendations available"])
    
    def detect_red_flags(self, violations: List[Violation]) -> List[Violation]:
        """
        Detect red flag violations regardless of score.
        
        Args:
            violations: List of violations to check
            
        Returns:
            List of red flag violations
        """
        return [v for v in violations if v.rule_name in self.red_flag_rules]
    
    def get_refactoring_suggestions(self, violations: List[Violation]) -> Dict[str, List[str]]:
        """
        Get refactoring suggestions based on violations.
        
        Args:
            violations: List of violations to analyze
            
        Returns:
            Dictionary mapping rule names to suggestion lists
        """
        suggestions = {
            'External Dependency Count': [
                "Use dependency injection to make dependencies explicit",
                "Create interfaces for external systems",
                "Mock external dependencies in tests"
            ],
            'Direct File I/O in Logic': [
                "Separate file operations from business logic",
                "Use repository pattern for data access",
                "Pass file handles as parameters instead of opening inside functions"
            ],
            'Non-Deterministic Time Usage': [
                "Inject time as a parameter for testing",
                "Use time abstraction layer",
                "Avoid time-based logic in business rules"
            ],
            'Randomness Usage': [
                "Inject random number generator as parameter",
                "Use deterministic seeds for testing",
                "Separate random logic from business logic"
            ],
            'Global State Mutation': [
                "Use dependency injection instead of globals",
                "Create stateless functions when possible",
                "Encapsulate state in objects with clear interfaces"
            ],
            'Mixed I/O and Logic': [
                "Separate I/O operations from business logic",
                "Use command/query separation pattern",
                "Create pure functions for business logic"
            ],
            'Branch Explosion Risk': [
                "Extract complex conditions into separate functions",
                "Use strategy pattern for complex branching",
                "Consider lookup tables instead of complex conditionals"
            ],
            'Exception-Driven Control Flow': [
                "Use return values or status codes instead of exceptions",
                "Validate inputs before processing",
                "Handle expected errors without exceptions"
            ],
            'Constructor Side Effects': [
                "Move side effects to separate methods",
                "Use factory pattern for complex initialization",
                "Keep constructors simple and focused"
            ],
            'Hidden Dependencies via Imports-in-Function': [
                "Move imports to module level",
                "Document all dependencies explicitly",
                "Use dependency injection for better testability"
            ],
            'Excessive Parameter Count': [
                "Group related parameters into objects",
                "Use configuration objects for many options",
                "Consider method chaining for complex operations"
            ],
            'Low Observability': [
                "Add meaningful return values",
                "Include logging for important operations",
                "Add assertions for critical invariants",
                "Make side effects explicit and observable"
            ]
        }
        
        result = {}
        for violation in violations:
            rule_suggestions = suggestions.get(violation.rule_name, [])
            if rule_suggestions:
                result[violation.rule_name] = rule_suggestions
        
        return result
