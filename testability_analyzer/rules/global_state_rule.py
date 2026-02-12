"""
Global State Mutation rule implementation.

Detects global variable modifications and applies -10 points per function.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class GlobalStateRule(TestabilityRule):
    """Rule that detects global state mutations in functions."""
    
    def __init__(self):
        self._global_state_patterns = {
            'module_level_vars': True,
            'class_level_vars': True,
            'singleton_modifications': True,
            'registry_modifications': True
        }
    
    @property
    def rule_name(self) -> str:
        return "Global State Mutation"
    
    @property
    def penalty_points(self) -> int:
        return 10
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for global state mutations.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context containing global variables and imports
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        
        # Look for global state mutations in function body
        for child in ast.walk(node):
            if self._contains_global_mutation(child, context):
                violation = Violation(
                    rule_name=self.rule_name,
                    description="Global state mutation makes testing unpredictable",
                    points_deducted=self.penalty_points,
                    line_number=getattr(child, 'lineno', node.lineno),
                    function_name=node.name,
                    is_red_flag=True  # Global state mutation is always a red flag
                )
                violations.append(violation)
                break  # One violation per function is sufficient
        
        return violations
    
    def _contains_global_mutation(self, node: ast.AST, context: Any) -> bool:
        """
        Check if an AST node contains global state mutations.
        
        Args:
            node: AST node to check
            context: Analysis context with global variables
            
        Returns:
            True if node contains global state mutations
        """
        # Check for explicit global declarations
        if isinstance(node, ast.Global):
            return True
        
        # Check for assignments to global variables
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if self._is_global_assignment(target, context):
                    return True
        
        # Check for augmented assignments to globals
        if isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                if hasattr(context, 'global_variables') and node.target.id in context.global_variables:
                    return True
        
        # Check for attribute assignments that might be global state
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                # Check for module-level attribute modifications
                if node.value.id in ['os', 'sys', 'config', 'settings', 'globals']:
                    return True
        
        # Check for function calls that modify global state
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    # Check for registry modifications, singleton updates, etc.
                    if node.func.attr in ['register', 'unregister', 'update', 'set', 'clear', 'append', 'extend']:
                        if node.func.value.id in ['registry', 'cache', 'pool', 'manager']:
                            return True
        
        return False
    
    def _is_global_assignment(self, target: ast.AST, context: Any) -> bool:
        """
        Check if an assignment target is a global variable.
        
        Args:
            target: Assignment target to check
            context: Analysis context
            
        Returns:
            True if target is a global variable
        """
        if isinstance(target, ast.Name):
            # Check if this is a known global variable
            if hasattr(context, 'global_variables') and target.id in context.global_variables:
                return True
            
            # Check if this is a module-level import (common global pattern)
            if hasattr(context, 'imports'):
                for import_name in context.imports:
                    if target.id == import_name.split('.')[0]:
                        return True
        
        elif isinstance(target, ast.Attribute):
            # Check for attribute assignment to global objects
            if isinstance(target.value, ast.Name):
                if target.value.id in ['os', 'sys', 'config', 'settings']:
                    return True
        
        return False
