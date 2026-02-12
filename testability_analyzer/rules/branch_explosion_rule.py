"""
Branch Explosion Risk rule implementation.

Detects excessive branching and applies -2 points per branch after the first 3.
"""

import ast
from typing import List, Any

from ..base import TestabilityRule, Violation


class BranchExplosionRule(TestabilityRule):
    """Rule that detects excessive branching complexity in functions."""
    
    def __init__(self):
        self._branch_threshold = 3  # First 3 branches are free
        self._penalty_per_branch = 2
    
    @property
    def rule_name(self) -> str:
        return "Branch Explosion Risk"
    
    @property
    def penalty_points(self) -> int:
        return 2  # Per branch after threshold
    
    def evaluate(self, node: ast.AST, context: Any) -> List[Violation]:
        """
        Evaluate a function for branch explosion risk.
        
        Args:
            node: AST node to evaluate (should be FunctionDef or AsyncFunctionDef)
            context: Analysis context
            
        Returns:
            List of violations found
        """
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
        
        violations = []
        
        # Count all branching structures
        branch_count = self._count_branches(node)
        
        # Apply penalty for branches beyond threshold
        if branch_count > self._branch_threshold:
            excess_branches = branch_count - self._branch_threshold
            total_penalty = excess_branches * self.penalty_points
            
            violation = Violation(
                rule_name=self.rule_name,
                description=f"Excessive branching: {branch_count} branches (threshold: {self._branch_threshold})",
                points_deducted=total_penalty,
                line_number=node.lineno,
                function_name=node.name,
                is_red_flag=False
            )
            violations.append(violation)
        
        return violations
    
    def _count_branches(self, node: ast.AST) -> int:
        """
        Count branching structures in a function.
        
        Args:
            node: Function node to analyze
            
        Returns:
            Total number of branching structures
        """
        branch_count = 0
        
        for child in ast.walk(node):
            # Count if statements
            if isinstance(child, ast.If):
                branch_count += 1
                # Count elif branches
                if hasattr(child, 'orelse') and child.orelse:
                    for elif_node in child.orelse:
                        if isinstance(elif_node, ast.If):
                            branch_count += 1
            
            # Count for loops
            elif isinstance(child, (ast.For, ast.AsyncFor)):
                branch_count += 1
            
            # Count while loops
            elif isinstance(child, (ast.While, ast.AsyncWhile)):
                branch_count += 1
            
            # Count try-except blocks
            elif isinstance(child, ast.Try):
                branch_count += 1
                # Count except handlers
                branch_count += len(child.handlers)
            
            # Count conditional expressions (ternary operators)
            elif isinstance(child, ast.IfExp):
                branch_count += 1
            
            # Count match statements (Python 3.10+)
            elif hasattr(ast, 'Match') and isinstance(child, ast.Match):
                branch_count += 1
                # Count case patterns
                if hasattr(child, 'cases'):
                    branch_count += len(child.cases)
        
        return branch_count
    
    def _get_branch_details(self, node: ast.AST) -> List[str]:
        """
        Get detailed information about branches for reporting.
        
        Args:
            node: Function node to analyze
            
        Returns:
            List of branch descriptions
        """
        branches = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                branches.append(f"if statement at line {child.lineno}")
            elif isinstance(child, (ast.For, ast.AsyncFor)):
                branches.append(f"for loop at line {child.lineno}")
            elif isinstance(child, (ast.While, ast.AsyncWhile)):
                branches.append(f"while loop at line {child.lineno}")
            elif isinstance(child, ast.Try):
                branches.append(f"try-except block at line {child.lineno}")
            elif isinstance(child, ast.IfExp):
                branches.append(f"ternary expression at line {child.lineno}")
            elif hasattr(ast, 'Match') and isinstance(child, ast.Match):
                branches.append(f"match statement at line {child.lineno}")
        
        return branches
