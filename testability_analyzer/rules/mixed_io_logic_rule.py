"""
Mixed I/O and Logic rule implementation.

Detects functions that mix I/O operations with business logic and applies -8 points.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class MixedIOLogicRule(TestabilityRule):
    """Rule that detects mixed I/O and business logic in functions."""
    
    def __init__(self):
        self._io_operations = {
            'file_ops': {'open', 'read', 'write', 'close', 'seek', 'tell', 'remove', 'mkdir'},
            'network_ops': {'requests', 'urlopen', 'connect', 'send', 'receive'},
            'console_ops': {'print', 'input', 'raw_input'},
            'db_ops': {'execute', 'fetch', 'commit', 'rollback', 'cursor'},
            'http_ops': {'get', 'post', 'put', 'delete', 'patch', 'head', 'options'}
        }
        
        self._io_modules = {
            'os', 'pathlib', 'shutil', 'io', 'tempfile',
            'requests', 'urllib', 'socket', 'http', 'https',
            'sqlite3', 'psycopg2', 'mysql', 'mongodb'
        }
    
    @property
    def rule_name(self) -> str:
        return "Mixed I/O and Logic"
    
    @property
    def penalty_points(self) -> int:
        return 8
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for mixed I/O and logic operations.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []

        # Don't flag pure I/O helper functions by name (integration tests treat these as acceptable).
        if self._is_pure_io_function(node):
            return []
        
        # Check for mixed I/O and logic
        io_operations = self._count_io_operations(node)
        logic_operations = self._count_logic_operations(node)
        
        if io_operations > 0 and logic_operations > 0:
            violation = Violation(
                rule_name=self.rule_name,
                description="Mixed I/O and business logic makes testing difficult",
                points_deducted=self.penalty_points,
                line_number=node.lineno,
                function_name=node.name,
                is_red_flag=True  # Mixed I/O and logic is always a red flag
            )
            return [violation]
        
        return []
    
    def _is_pure_io_function(self, node: ast.AST) -> bool:
        """
        Check if function is primarily for I/O operations.
        
        Args:
            node: Function node to check
            
        Returns:
            True if function appears to be pure I/O
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
        
        function_name = node.name.lower()
        io_indicators = [
            'read', 'write', 'open', 'close',
            'fetch', 'send', 'receive', 'connect', 'download',
            'upload', 'import', 'export', 'print', 'display'
        ]
        
        return any(indicator in function_name for indicator in io_indicators)
    
    def _is_pure_logic_function(self, node: ast.AST) -> bool:
        """
        Check if function is primarily for business logic.
        
        Args:
            node: Function node to check
            
        Returns:
            True if function appears to be pure logic
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
        
        function_name = node.name.lower()
        logic_indicators = [
            'calculate', 'compute', 'process', 'transform', 'validate',
            'check', 'verify', 'analyze', 'evaluate', 'determine',
            'convert', 'format', 'parse', 'filter', 'sort'
        ]
        
        return any(indicator in function_name for indicator in logic_indicators)
    
    def _count_io_operations(self, node: ast.AST) -> int:
        """
        Count I/O operations in a function.
        
        Args:
            node: Function node to analyze
            
        Returns:
            Number of I/O operations found
        """
        io_count = 0
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in self._io_operations['file_ops'] or \
                       child.func.id in self._io_operations['console_ops']:
                        io_count += 1
                
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        module_name = child.func.value.id
                        method_name = child.func.attr
                        
                        if module_name in self._io_modules:
                            io_count += 1
        
        return io_count
    
    def _count_logic_operations(self, node: ast.AST) -> int:
        """
        Count business logic operations in a function.
        
        Args:
            node: Function node to analyze
            
        Returns:
            Number of logic operations found
        """
        logic_count = 0
        
        for child in ast.walk(node):
            # Count control flow structures
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                logic_count += 1
            
            # Count arithmetic operations
            elif isinstance(child, ast.BinOp):
                if isinstance(child.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)):
                    logic_count += 1
            
            # Count comparisons
            elif isinstance(child, ast.Compare):
                logic_count += 1
            
            # Count non-I/O free function calls as logic (e.g., calculate_complex_logic()).
            # Do not treat attribute calls on local variables (e.g., data.upper()) as business logic.
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id not in self._io_operations['file_ops'] and \
                       child.func.id not in self._io_operations['console_ops']:
                        logic_count += 1
        
        return logic_count
