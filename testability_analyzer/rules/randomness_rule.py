"""
Randomness Usage rule implementation.

Detects random number generators and applies -10 points per function.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class RandomnessRule(TestabilityRule):
    """Rule that detects randomness usage in functions."""
    
    def __init__(self):
        self._random_functions = {
            'random.random', 'random.randint', 'random.randrange', 'random.choice',
            'random.shuffle', 'random.sample', 'random.uniform', 'random.triangular',
            'random.betavariate', 'random.expovariate', 'random.gammavariate',
            'random.gauss', 'random.lognormvariate', 'random.normalvariate',
            'random.paretovariate', 'random.vonmisesvariate', 'random.weibullvariate',
            'random.getrandbits', 'random.seed', 'random.getstate', 'random.setstate',
            'numpy.random.random', 'numpy.random.randint', 'numpy.random.rand',
            'numpy.random.randn', 'numpy.random.choice', 'numpy.random.shuffle',
            'numpy.random.uniform', 'numpy.random.normal', 'numpy.random.binomial',
            'numpy.random.poisson', 'numpy.random.exponential',
            'secrets.randbelow', 'secrets.choice', 'secrets.token_bytes',
            'secrets.token_hex', 'secrets.token_urlsafe', 'secrets.compare_digest',
            'uuid.uuid1', 'uuid.uuid3', 'uuid.uuid4', 'uuid.uuid5',
            'os.urandom', 'os.getrandom'
        }
        
        self._random_modules = {'random', 'numpy', 'secrets', 'uuid', 'os'}
    
    @property
    def rule_name(self) -> str:
        return "Randomness Usage"
    
    @property
    def penalty_points(self) -> int:
        return 10
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for randomness operations.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        
        # Look for randomness operations in function body
        for child in ast.walk(node):
            if self._contains_random_operation(child):
                violation = Violation(
                    rule_name=self.rule_name,
                    description="Randomness usage makes testing non-deterministic",
                    points_deducted=self.penalty_points,
                    line_number=getattr(child, 'lineno', node.lineno),
                    function_name=node.name,
                    is_red_flag=True  # Randomness is always a red flag
                )
                violations.append(violation)
                break  # One violation per function is sufficient
        
        return violations
    
    def _contains_random_operation(self, node: ast.AST) -> bool:
        """
        Check if an AST node contains randomness-related operations.
        
        Args:
            node: AST node to check
            
        Returns:
            True if node contains randomness operations
        """
        # Check for direct random function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ['random', 'randint', 'choice', 'shuffle']:
                    return True
            
            elif isinstance(node.func, ast.Attribute):
                # Check method calls like random.random(), numpy.random.rand()
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                    method_name = node.func.attr
                    
                    if module_name in self._random_modules:
                        full_call = f"{module_name}.{method_name}"
                        if full_call in self._random_functions:
                            return True
                
                # Check chained calls like numpy.random.random()
                elif isinstance(node.func.value, ast.Attribute):
                    if isinstance(node.func.value.value, ast.Name):
                        module_name = node.func.value.value.id
                        class_name = node.func.value.attr
                        method_name = node.func.attr
                        
                        if module_name in self._random_modules:
                            full_call = f"{module_name}.{class_name}.{method_name}"
                            if full_call in self._random_functions:
                                return True
        
        # Check for random module imports in the function body
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    if alias.name in self._random_modules:
                        return True
            elif isinstance(child, ast.ImportFrom):
                if child.module and child.module in self._random_modules:
                    return True
        
        return False
