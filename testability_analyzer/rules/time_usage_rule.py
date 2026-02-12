"""
Non-Deterministic Time Usage rule implementation.

Detects time-dependent functions and applies -10 points per function.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class TimeUsageRule(TestabilityRule):
    """Rule that detects non-deterministic time usage in functions."""
    
    def __init__(self):
        self._time_functions = {
            'time.time', 'time.sleep', 'time.monotonic', 'time.perf_counter',
            'time.process_time', 'time.thread_time', 'time.time_ns',
            'datetime.now', 'datetime.today', 'datetime.utcnow',
            'datetime.timestamp', 'date.today', 'datetime.datetime.now',
            'datetime.datetime.today', 'datetime.datetime.utcnow'
        }
        
        self._time_modules = {'time', 'datetime', 'date'}
    
    @property
    def rule_name(self) -> str:
        return "Non-Deterministic Time Usage"
    
    @property
    def penalty_points(self) -> int:
        return 10
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for time usage operations.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        
        # Look for time operations in function body
        for child in ast.walk(node):
            if self._contains_time_operation(child):
                violation = Violation(
                    rule_name=self.rule_name,
                    description="Non-deterministic time usage makes testing difficult",
                    points_deducted=self.penalty_points,
                    line_number=getattr(child, 'lineno', node.lineno),
                    function_name=node.name,
                    is_red_flag=True  # Time usage is always a red flag
                )
                violations.append(violation)
                break  # One violation per function is sufficient
        
        return violations
    
    def _contains_time_operation(self, node: ast.AST) -> bool:
        """
        Check if an AST node contains time-related operations.
        
        Args:
            node: AST node to check
            
        Returns:
            True if node contains time operations
        """
        # Check for direct time function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self._time_functions:
                    return True
            
            elif isinstance(node.func, ast.Attribute):
                # Check method calls like time.time(), datetime.now()
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                    method_name = node.func.attr
                    
                    if module_name in self._time_modules:
                        full_call = f"{module_name}.{method_name}"
                        if full_call in self._time_functions:
                            return True
                
                # Check chained calls like datetime.datetime.now()
                elif isinstance(node.func.value, ast.Attribute):
                    if isinstance(node.func.value.value, ast.Name):
                        module_name = node.func.value.value.id
                        class_name = node.func.value.attr
                        method_name = node.func.attr
                        
                        if module_name in self._time_modules:
                            full_call = f"{module_name}.{class_name}.{method_name}"
                            if full_call in self._time_functions:
                                return True
        
        # Check for time module imports in the function body
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    if alias.name in self._time_modules:
                        return True
            elif isinstance(child, ast.ImportFrom):
                if child.module and child.module in self._time_modules:
                    return True
        
        return False
