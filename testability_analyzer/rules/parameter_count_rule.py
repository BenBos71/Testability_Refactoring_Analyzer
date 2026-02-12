"""
Excessive Parameter Count rule implementation.

Detects functions with too many parameters and applies -5 points per function.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class ParameterCountRule(TestabilityRule):
    """Rule that detects excessive parameter counts in functions."""
    
    def __init__(self):
        self._parameter_threshold = 5  # Maximum allowed parameters
        self._self_param_exempt = True  # Don't count 'self' parameter
    
    @property
    def rule_name(self) -> str:
        return "Excessive Parameter Count"
    
    @property
    def penalty_points(self) -> int:
        return 5
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for excessive parameter count.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        
        # Count parameters (excluding 'self' for methods)
        param_count = self._count_effective_parameters(node)
        
        if param_count > self._parameter_threshold:
            violation = Violation(
                rule_name=self.rule_name,
                description=f"Excessive parameters: {param_count} (threshold: {self._parameter_threshold})",
                points_deducted=self.penalty_points,
                line_number=node.lineno,
                function_name=node.name,
                is_red_flag=False
            )
            violations.append(violation)
        
        return violations
    
    def _count_effective_parameters(self, node: ast.AST) -> int:
        """
        Count effective parameters in a function.
        
        Args:
            node: Function node to analyze
            
        Returns:
            Number of effective parameters
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return 0
        
        effective_params = 0
        
        # Count positional arguments
        for arg in node.args.args:
            if not self._should_ignore_parameter(arg.arg):
                effective_params += 1
        
        # Count positional-only arguments (Python 3.8+)
        if hasattr(node.args, 'posonlyargs'):
            for arg in node.args.posonlyargs:
                if not self._should_ignore_parameter(arg.arg):
                    effective_params += 1
        
        # Count keyword-only arguments
        for arg in node.args.kwonlyargs:
            if not self._should_ignore_parameter(arg.arg):
                effective_params += 1
        
        # Count *args (counts as 1 parameter)
        if node.args.vararg and not self._should_ignore_parameter(node.args.vararg.arg):
            effective_params += 1
        
        # Count **kwargs (counts as 1 parameter)
        if node.args.kwarg and not self._should_ignore_parameter(node.args.kwarg.arg):
            effective_params += 1
        
        return effective_params
    
    def _should_ignore_parameter(self, param_name: str) -> bool:
        """
        Check if a parameter should be ignored in the count.
        
        Args:
            param_name: Parameter name to check
            
        Returns:
            True if parameter should be ignored
        """
        return self._self_param_exempt and param_name == 'self'
    
    def _get_parameter_details(self, node: ast.AST) -> dict:
        """
        Get detailed information about function parameters.
        
        Args:
            node: Function node to analyze
            
        Returns:
            Dictionary with parameter details
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return {}
        
        details = {
            'positional': [],
            'positional_only': [],
            'keyword_only': [],
            'varargs': None,
            'kwargs': None,
            'defaults': len(node.args.defaults) if node.args.defaults else 0
        }
        
        # Positional arguments
        for arg in node.args.args:
            details['positional'].append(arg.arg)
        
        # Positional-only arguments (Python 3.8+)
        if hasattr(node.args, 'posonlyargs'):
            for arg in node.args.posonlyargs:
                details['positional_only'].append(arg.arg)
        
        # Keyword-only arguments
        for arg in node.args.kwonlyargs:
            details['keyword_only'].append(arg.arg)
        
        # *args
        if node.args.vararg:
            details['varargs'] = node.args.vararg.arg
        
        # **kwargs
        if node.args.kwarg:
            details['kwargs'] = node.args.kwarg.arg
        
        return details
