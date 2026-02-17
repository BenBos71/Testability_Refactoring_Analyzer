"""
Direct File I/O in Logic rule implementation.

Detects file I/O operations in non-I/O-specific functions and applies -10 points.
"""

import ast
import re
from typing import List, Any

from ..base import TestabilityRule, Violation


class FileIORule(TestabilityRule):
    """Rule that detects direct file I/O in business logic."""
    
    def __init__(self):
        self._io_functions = {
            'open', 'read', 'write', 'close', 'seek', 'tell',
            'remove', 'mkdir', 'rmdir', 'exists', 'isfile', 'isdir',
            'listdir', 'scandir', 'walk', 'glob', 'rglob'
        }
        
        self._io_modules = {'os', 'pathlib', 'shutil', 'io', 'tempfile'}
        
        self._io_classes = {
            'Path', 'PurePath', 'PosixPath', 'WindowsPath',
            'FileIO', 'TextIOWrapper', 'BufferedReader', 'BufferedWriter',
            'TemporaryFile', 'NamedTemporaryFile'
        }
    
    @property
    def rule_name(self) -> str:
        return "Direct File I/O in Logic"
    
    @property
    def penalty_points(self) -> int:
        return 10
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for file I/O operations.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        # Check if function name suggests it's I/O related
        if self._is_io_function_name(node.name):
            return []  # Skip functions whose primary purpose is I/O
        
        violations = []
        
        # Look for I/O operations in function body
        for child in ast.walk(node):
            if self._contains_io_operation(child):
                violation = Violation(
                    rule_name=self.rule_name,
                    description="Direct file I/O in business logic",
                    points_deducted=self.penalty_points,
                    line_number=getattr(child, 'lineno', node.lineno),
                    function_name=node.name,
                    is_red_flag=False
                )
                violations.append(violation)
                break  # One violation per function is sufficient
        
        return violations
    
    def _is_io_function_name(self, function_name: str) -> bool:
        """
        Check if function name suggests its primary purpose is I/O.
        
        Args:
            function_name: Name of the function to check
            
        Returns:
            True if function appears to be I/O related
        """
        io_indicators = [
            'read', 'write',
            'file', 'dir', 'path', 'io', 'temp'
        ]
        
        name = function_name.lower()
        tokens = [t for t in re.split(r"[^a-z0-9]+", name) if t]
        return any(indicator in tokens for indicator in io_indicators)
    
    def _contains_io_operation(self, node: ast.AST) -> bool:
        """
        Check if an AST node contains file I/O operations.
        
        Args:
            node: AST node to check
            
        Returns:
            True if node contains I/O operations
        """
        # Check for direct I/O function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self._io_functions:
                    return True
            
            elif isinstance(node.func, ast.Attribute):
                # Check method calls on I/O objects
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in self._io_classes:
                        return True
        
        # Check for I/O module usage
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if child.id in self._io_modules:
                    return True
        
        return False
