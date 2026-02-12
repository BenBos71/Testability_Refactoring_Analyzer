"""
External Dependency Count rule implementation.

Detects distinct external dependency types and applies -5 points per distinct type.
"""

import ast
from typing import List, Set, Any

from ..base import TestabilityRule, Violation


class ExternalDependencyRule(TestabilityRule):
    """Rule that detects external dependencies in functions."""
    
    def __init__(self):
        self._dependency_types = {
            'file_system': {
                'functions': {'open', 'read', 'write', 'remove', 'mkdir', 'rmdir', 'exists', 'isfile', 'isdir'},
                'modules': {'os', 'pathlib', 'shutil'}
            },
            'environment': {
                'functions': {'getenv', 'environ'},
                'modules': {'os'}
            },
            'network': {
                'functions': {'requests', 'urlopen', 'urllib.request', 'socket', 'connect'},
                'modules': {'requests', 'urllib', 'socket', 'http', 'https'}
            },
            'os_level': {
                'functions': {'subprocess', 'system', 'exec', 'popen'},
                'modules': {'subprocess', 'os', 'sys'}
            },
            'singletons': {
                'functions': {'getInstance', 'instance', 'current'},
                'modules': {'logging', 'threading', 'multiprocessing'}
            }
        }
    
    @property
    def rule_name(self) -> str:
        return "External Dependency Count"
    
    @property
    def penalty_points(self) -> int:
        return 5
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for external dependencies.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        detected_types = set()
        
        # Get all function calls in the function body
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                dep_type = self._classify_dependency(child)
                if dep_type:
                    detected_types.add(dep_type)
        
        # Apply penalty for each distinct dependency type
        for dep_type in detected_types:
            violation = Violation(
                rule_name=self.rule_name,
                description=f"External dependency: {dep_type}",
                points_deducted=self.penalty_points,
                line_number=node.lineno,
                function_name=node.name,
                is_red_flag=False
            )
            violations.append(violation)
        
        return violations
    
    def _classify_dependency(self, call_node: ast.Call) -> str:
        """
        Classify a function call as a dependency type.
        
        Args:
            call_node: AST Call node to classify
            
        Returns:
            Dependency type as string or None if not external
        """
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id
            
            # Check if this is an imported function
            if hasattr(call_node, 'import_context') and func_name in call_node.import_context:
                return None  # Local function, not external
            
            # Check against known dependency types
            for dep_type, config in self._dependency_types.items():
                if func_name in config['functions']:
                    return dep_type.replace('_', ' ').title()
                
                # Check if function name contains module indicators
                if any(module in func_name for module in config['modules']):
                    return dep_type.replace('_', ' ').title()
        
        elif isinstance(call_node.func, ast.Attribute):
            # Handle method calls like module.function()
            if isinstance(call_node.func.value, ast.Name):
                module_name = call_node.func.value.id
                method_name = call_node.func.attr
                
                for dep_type, config in self._dependency_types.items():
                    if module_name in config['modules']:
                        return dep_type.replace('_', ' ').title()
        
        return None
