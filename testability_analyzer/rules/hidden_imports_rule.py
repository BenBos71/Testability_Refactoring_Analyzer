"""
Hidden Dependencies via Imports-in-Function rule implementation.

Detects import statements inside functions and applies -5 points per function.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class HiddenImportsRule(TestabilityRule):
    """Rule that detects hidden dependencies via imports inside functions."""
    
    def __init__(self):
        self._allowed_imports = {
            # Standard library imports commonly used for specific purposes
            'typing', 'collections', 'itertools', 'functools',
            'datetime', 're', 'json', 'csv', 'math', 'random'
        }
    
    @property
    def rule_name(self) -> str:
        return "Hidden Dependencies via Imports-in-Function"
    
    @property
    def penalty_points(self) -> int:
        return 5
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for hidden imports.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        
        # Look for import statements inside function body
        for child in ast.walk(node):
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                # Check if this is a problematic import
                if self._is_problematic_import(child):
                    violation = Violation(
                        rule_name=self.rule_name,
                        description="Hidden dependency via import inside function",
                        points_deducted=self.penalty_points,
                        line_number=child.lineno,
                        function_name=node.name,
                        is_red_flag=False
                    )
                    violations.append(violation)
                    break  # One violation per function is sufficient
        
        return violations
    
    def _is_problematic_import(self, import_node: ast.AST) -> bool:
        """
        Check if an import statement is problematic.
        
        Args:
            import_node: Import or ImportFrom node to check
            
        Returns:
            True if import is problematic
        """
        if isinstance(import_node, ast.Import):
            for alias in import_node.names:
                module_name = alias.name
                if self._is_external_dependency(module_name):
                    return True
        
        elif isinstance(import_node, ast.ImportFrom):
            if import_node.module:
                module_name = import_node.module
                if self._is_external_dependency(module_name):
                    return True
        
        return False
    
    def _is_external_dependency(self, module_name: str) -> bool:
        """
        Check if a module is an external dependency.
        
        Args:
            module_name: Module name to check
            
        Returns:
            True if module is external dependency
        """
        # Get the top-level module name
        top_level = module_name.split('.')[0]
        
        # Check if it's in allowed standard library modules
        if top_level in self._allowed_imports:
            return False
        
        # Check if it's a known external dependency
        external_indicators = [
            'requests', 'numpy', 'pandas', 'scipy', 'matplotlib',
            'flask', 'django', 'fastapi', 'sqlalchemy', 'pytest',
            'click', 'black', 'pylint', 'mypy', 'setuptools'
        ]
        
        return top_level in external_indicators
    
    def _get_import_details(self, import_node: ast.AST) -> str:
        """
        Get details about the import statement.
        
        Args:
            import_node: Import or ImportFrom node
            
        Returns:
            String description of the import
        """
        if isinstance(import_node, ast.Import):
            imports = []
            for alias in import_node.names:
                if alias.asname:
                    imports.append(f"{alias.name} as {alias.asname}")
                else:
                    imports.append(alias.name)
            return f"import {', '.join(imports)}"
        
        elif isinstance(import_node, ast.ImportFrom):
            imports = []
            for alias in import_node.names:
                if alias.asname:
                    imports.append(f"{alias.name} as {alias.asname}")
                else:
                    imports.append(alias.name)
            return f"from {import_node.module} import {', '.join(imports)}"
        
        return "unknown import"
