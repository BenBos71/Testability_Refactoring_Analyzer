"""
Constructor Side Effects rule implementation.

Detects constructor side effects and applies -15 points per class.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class ConstructorSideEffectsRule(TestabilityRule):
    """Rule that detects side effects in class constructors."""
    
    def __init__(self):
        self._side_effect_operations = {
            'file_ops': {'open', 'write', 'read', 'remove', 'mkdir'},
            'network_ops': {'connect', 'send', 'receive', 'request'},
            'db_ops': {'execute', 'commit', 'cursor', 'connect'},
            'process_ops': {'start', 'stop', 'kill', 'run'},
            'thread_ops': {'start', 'join', 'lock', 'acquire'},
            'global_state': {'register', 'unregister', 'update', 'modify'}
        }
        
        self._side_effect_modules = {
            'os', 'pathlib', 'shutil', 'requests', 'urllib', 'socket',
            'sqlite3', 'psycopg2', 'mysql', 'threading', 'multiprocessing',
            'logging', 'subprocess', 'sys'
        }
    
    @property
    def rule_name(self) -> str:
        return "Constructor Side Effects"
    
    @property
    def penalty_points(self) -> int:
        return 15
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a class constructor for side effects.
        
        Args:
            node: AST node to evaluate (should be ClassDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, ast.ClassDef):
            return []
        
        violations = []
        
        # Find the __init__ method
        init_method = None
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                init_method = item
                break
        
        if init_method and self._has_constructor_side_effects(init_method):
            violation = Violation(
                rule_name=self.rule_name,
                description="Constructor has side effects that make testing difficult",
                points_deducted=self.penalty_points,
                line_number=init_method.lineno,
                function_name=f"{node.name}.__init__",
                is_red_flag=True  # Constructor side effects are always a red flag
            )
            violations.append(violation)
        
        return violations
    
    def _has_constructor_side_effects(self, init_method: ast.FunctionDef) -> bool:
        """
        Check if __init__ method has side effects.
        
        Args:
            init_method: __init__ method to analyze
            
        Returns:
            True if constructor has side effects
        """
        # Check for side effect operations in __init__
        for child in ast.walk(init_method):
            if self._contains_side_effect_operation(child):
                return True
        
        return False
    
    def _contains_side_effect_operation(self, node: ast.AST) -> bool:
        """
        Check if an AST node contains side effect operations.
        
        Args:
            node: AST node to check
            
        Returns:
            True if node contains side effects
        """
        # Check for function calls that might have side effects
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                # Direct function calls
                if node.func.id in self._side_effect_operations['file_ops'] or \
                   node.func.id in self._side_effect_operations['network_ops'] or \
                   node.func.id in self._side_effect_operations['db_ops'] or \
                   node.func.id in self._side_effect_operations['process_ops'] or \
                   node.func.id in self._side_effect_operations['thread_ops'] or \
                   node.func.id in self._side_effect_operations['global_state']:
                    return True
            
            elif isinstance(node.func, ast.Attribute):
                # Method calls
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                    method_name = node.func.attr
                    
                    if module_name in self._side_effect_modules:
                        return True
                    
                    # Check for specific side effect methods
                    if method_name in ['open', 'write', 'read', 'connect', 'start', 'stop', 
                                    'register', 'unregister', 'update', 'modify', 'execute',
                                    'commit', 'cursor', 'send', 'receive']:
                        return True
        
        # Check for assignments to global state
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if isinstance(target.value, ast.Name):
                        if target.value.id in ['registry', 'cache', 'pool', 'manager', 'globals']:
                            return True
        
        # Check for imports in __init__ (can have side effects)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return True
        
        # Check for thread/process creation
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ['Thread', 'Process', 'Pool', 'Lock', 'Semaphore']:
                    return True
        
        return False
    
    def _get_side_effect_details(self, init_method: ast.FunctionDef) -> List[str]:
        """
        Get details about side effects found in constructor.
        
        Args:
            init_method: __init__ method to analyze
            
        Returns:
            List of side effect descriptions
        """
        side_effects = []
        
        for child in ast.walk(init_method):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    side_effects.append(f"Function call: {child.func.id} at line {child.lineno}")
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        side_effects.append(f"Method call: {child.func.value.id}.{child.func.attr} at line {child.lineno}")
        
        return side_effects
