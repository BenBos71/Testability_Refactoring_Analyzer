"""
Exception-Driven Control Flow rule implementation.

Detects functions that use exceptions for control flow and applies -5 points.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class ExceptionControlFlowRule(TestabilityRule):
    """Rule that detects exception-driven control flow in functions."""
    
    def __init__(self):
        self._control_flow_exceptions = {
            'ValueError', 'TypeError', 'KeyError', 'IndexError', 'AttributeError',
            'StopIteration', 'LookupError', 'RuntimeError', 'AssertionError'
        }
        
        self._suspicious_patterns = {
            'empty_except': True,
            'broad_except': True,
            'exception_as_logic': True,
            'raise_in_except': True
        }
    
    @property
    def rule_name(self) -> str:
        return "Exception-Driven Control Flow"
    
    @property
    def penalty_points(self) -> int:
        return 5
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for exception-driven control flow.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        
        # Check for exception-driven control flow patterns
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                if self._is_exception_driven_control_flow(child):
                    violation = Violation(
                        rule_name=self.rule_name,
                        description="Exception-driven control flow makes testing difficult",
                        points_deducted=self.penalty_points,
                        line_number=child.lineno,
                        function_name=node.name,
                        is_red_flag=True  # Exception-driven control flow is always a red flag
                    )
                    violations.append(violation)
                    break  # One violation per function is sufficient
        
        return violations
    
    def _is_exception_driven_control_flow(self, try_node: ast.Try) -> bool:
        """
        Check if a try-except block is used for control flow.
        
        Args:
            try_node: Try node to analyze
            
        Returns:
            True if try-except is used for control flow
        """
        # Check for empty except blocks
        for handler in try_node.handlers:
            if self._is_empty_except_handler(handler):
                return True
        
        # Check for broad exception handling
        for handler in try_node.handlers:
            if self._is_broad_exception_handler(handler):
                return True
        
        # Check for control flow exceptions
        for handler in try_node.handlers:
            if self._uses_control_flow_exceptions(handler):
                return True
        
        # Check for exception-based loops
        if self._has_exception_based_loop(try_node):
            return True
        
        return False
    
    def _is_empty_except_handler(self, handler: ast.ExceptHandler) -> bool:
        """
        Check if an exception handler is empty or only contains pass.
        
        Args:
            handler: Exception handler to check
            
        Returns:
            True if handler is empty
        """
        if not handler.body:
            return True
        
        # Check if body only contains pass or comments
        for stmt in handler.body:
            if isinstance(stmt, ast.Pass):
                continue
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                # String literal (comment)
                continue
            else:
                return False
        
        return len(handler.body) > 0 and all(
            isinstance(stmt, (ast.Pass, ast.Expr)) for stmt in handler.body
        )
    
    def _is_broad_exception_handler(self, handler: ast.ExceptHandler) -> bool:
        """
        Check if an exception handler catches broad exceptions.
        
        Args:
            handler: Exception handler to check
            
        Returns:
            True if handler catches broad exceptions
        """
        # Bare except is always too broad
        if not handler.type:
            return True
        
        # Check for Exception or BaseException
        if isinstance(handler.type, ast.Name):
            if handler.type.id in ['Exception', 'BaseException']:
                return True
        
        # Check for tuple of exceptions that includes broad ones
        if isinstance(handler.type, ast.Tuple):
            for elt in handler.type.elts:
                if isinstance(elt, ast.Name) and elt.id in ['Exception', 'BaseException']:
                    return True
        
        return False
    
    def _uses_control_flow_exceptions(self, handler: ast.ExceptHandler) -> bool:
        """
        Check if handler catches exceptions typically used for control flow.
        
        Args:
            handler: Exception handler to check
            
        Returns:
            True if handler catches control flow exceptions
        """
        if not handler.type:
            return False
        
        # Check for specific control flow exceptions
        if isinstance(handler.type, ast.Name):
            if handler.type.id in self._control_flow_exceptions:
                return True
        
        # Check for tuple of exceptions
        if isinstance(handler.type, ast.Tuple):
            for elt in handler.type.elts:
                if isinstance(elt, ast.Name) and elt.id in self._control_flow_exceptions:
                    return True
        
        return False
    
    def _has_exception_based_loop(self, try_node: ast.Try) -> bool:
        """
        Check if try-except is used as a loop control mechanism.
        
        Args:
            try_node: Try node to analyze
            
        Returns:
            True if try-except is used for loop control
        """
        # Look for StopIteration being caught (common in iterator patterns)
        for handler in try_node.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == 'StopIteration':
                return True
        
        # Check if try block contains loop logic and except contains break/continue
        has_loop = False
        for stmt in try_node.body:
            if isinstance(stmt, (ast.For, ast.While)):
                has_loop = True
                break
        
        if has_loop:
            for handler in try_node.handlers:
                for stmt in handler.body:
                    if isinstance(stmt, (ast.Break, ast.Continue)):
                        return True
        
        return False
