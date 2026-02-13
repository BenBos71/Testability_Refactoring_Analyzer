"""
Low Observability rule implementation.

Detects functions with low observability and applies -5 points per function.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class ObservabilityRule(TestabilityRule):
    """Rule that detects functions with low observability."""
    
    def __init__(self):
        self._observability_indicators = {
            'return_statements': True,
            'logging_statements': True,
            'assertions': True,
            'side_effects': True
        }
        
        self._low_observability_patterns = {
            'no_return': True,
            'no_logging': True,
            'no_assertions': True,
            'void_functions': True
        }
    
    @property
    def rule_name(self) -> str:
        return "Low Observability"
    
    @property
    def penalty_points(self) -> int:
        return 5
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for low observability.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        
        # Check observability indicators
        observability_score = self._calculate_observability_score(node)
        
        if observability_score == 0:  # Low observability threshold - only flag if NO return, NO logging, AND NO assertions
            violation = Violation(
                rule_name=self.rule_name,
                description=f"Low observability: function lacks return values, logging, or assertions",
                points_deducted=self.penalty_points,
                line_number=node.lineno,
                function_name=node.name,
                is_red_flag=False
            )
            violations.append(violation)
        
        return violations
    
    def _calculate_observability_score(self, node: ast.AST) -> int:
        """
        Calculate observability score for a function.
        
        Args:
            node: Function node to analyze
            
        Returns:
            Observability score (0-4, higher is better)
        """
        score = 0
        
        # Check for return statements
        if self._has_return_statements(node):
            score += 1
        
        # Check for logging statements
        if self._has_logging_statements(node):
            score += 1
        
        # Check for assertions
        if self._has_assertions(node):
            score += 1
        
        # Check for meaningful side effects (that can be observed)
        if self._has_observable_side_effects(node):
            score += 1
        
        return score
    
    def _has_return_statements(self, node: ast.AST) -> bool:
        """
        Check if function has meaningful return statements.
        
        Args:
            node: Function node to analyze
            
        Returns:
            True if function has return statements
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                # Check if return has a value (not just bare return)
                if child.value is not None:
                    return True
        
        return False
    
    def _has_logging_statements(self, node: ast.AST) -> bool:
        """
        Check if function has logging statements.
        
        Args:
            node: Function node to analyze
            
        Returns:
            True if function has logging statements
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        module_name = child.func.value.id
                        method_name = child.func.attr
                        
                        # Check for logging calls
                        if module_name == 'logging' and method_name in ['debug', 'info', 'warning', 'error', 'critical']:
                            return True
                        
                        # Check for print statements (basic observability)
                        if module_name == 'print':
                            return True
                
                elif isinstance(child.func, ast.Name):
                    if child.func.id == 'print':
                        return True
        
        return False
    
    def _has_assertions(self, node: ast.AST) -> bool:
        """
        Check if function has assertion statements.
        
        Args:
            node: Function node to analyze
            
        Returns:
            True if function has assertions
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                return True
        
        return False
    
    def _has_observable_side_effects(self, node: ast.AST) -> bool:
        """
        Check if function has observable side effects.
        
        Args:
            node: Function node to analyze
            
        Returns:
            True if function has observable side effects
        """
        for child in ast.walk(node):
            # Check for file operations
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in ['write', 'print', 'save', 'commit']:
                        return True
                
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        method_name = child.func.attr
                        if method_name in ['write', 'save', 'commit', 'send', 'publish']:
                            return True
        
        return False
    
    def _get_observability_details(self, node: ast.AST) -> dict:
        """
        Get detailed observability information.
        
        Args:
            node: Function node to analyze
            
        Returns:
            Dictionary with observability details
        """
        return {
            'has_return': self._has_return_statements(node),
            'has_logging': self._has_logging_statements(node),
            'has_assertions': self._has_assertions(node),
            'has_side_effects': self._has_observable_side_effects(node),
            'score': self._calculate_observability_score(node)
        }
