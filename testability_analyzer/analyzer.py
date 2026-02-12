"""
Main analyzer implementation that orchestrates the static analysis pipeline.

Implements the Analyzer interface to coordinate AST parsing, rule evaluation,
scoring, and result aggregation.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any

from .base import Analyzer, FileScore, FunctionScore, ClassScore, Violation
from .ast_utils import parse_file, build_context
from .scoring import ScoreCalculator
from .rules import RuleRegistry
from .file_utils import find_python_files, filter_non_test_files
from .threshold_classifier import ThresholdClassifier


class TestabilityAnalyzer(Analyzer):
    """Main analyzer that implements the complete testability analysis pipeline."""
    
    def __init__(self):
        self.score_calculator = ScoreCalculator()
        self.rule_registry = RuleRegistry()
        self.threshold_classifier = ThresholdClassifier()
    
    def analyze_file(self, file_path: str) -> FileScore:
        """
        Analyze a single Python file for testability issues.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            FileScore with complete analysis results
        """
        # Parse the file
        tree = parse_file(file_path)
        if tree is None:
            # Return empty score for unparseable files
            return FileScore(
                file_path=file_path,
                overall_score=0,
                classification="Parse Error",
                function_scores=[],
                class_scores=[],
                red_flags=[]
            )
        
        # Build analysis context
        context = build_context(tree)
        
        # Extract functions and classes
        function_scores = self._analyze_functions(tree, context)
        class_scores = self._analyze_classes(tree, context)
        
        # Calculate overall file score
        all_scores = [score.final_score for score in function_scores]
        
        # Add method scores from classes
        for class_score in class_scores:
            for method_score in class_score.method_scores:
                all_scores.append(method_score.final_score)
        
        # Add constructor penalties
        for class_score in class_scores:
            constructor_penalty = sum(v.points_deducted for v in class_score.constructor_violations)
            if constructor_penalty > 0:
                # Constructor score is baseline minus penalties
                constructor_score = max(100 - constructor_penalty, 0)
                all_scores.append(constructor_score)
        
        if all_scores:
            overall_score = min(all_scores)  # Use worst score as file score
        else:
            overall_score = 100  # Empty file gets perfect score
        
        # Get classification
        classification = self.threshold_classifier.classify_file_score(overall_score)
        
        # Collect red flags
        red_flags = []
        for score in function_scores:
            red_flags.extend([v for v in score.violations if v.is_red_flag])
        for score in class_scores:
            red_flags.extend(score.constructor_violations)
        
        return FileScore(
            file_path=file_path,
            overall_score=overall_score,
            classification=classification,
            function_scores=function_scores,
            class_scores=class_scores,
            red_flags=red_flags
        )
    
    def analyze_directory(self, directory_path: str) -> List[FileScore]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            List of FileScore objects for all Python files
        """
        # Find all Python files (excluding test files)
        all_files = find_python_files([directory_path])
        python_files = filter_non_test_files(all_files)
        
        results = []
        for file_path in python_files:
            if file_path.is_file():
                result = self.analyze_file(str(file_path))
                results.append(result)
        
        return results
    
    def _analyze_functions(self, tree: ast.AST, context: Any) -> List[FunctionScore]:
        """
        Analyze all functions in the AST.
        
        Args:
            tree: The AST to analyze
            context: Analysis context
            
        Returns:
            List of FunctionScore objects
        """
        function_scores = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Evaluate all rules for this function
                violations = []
                for rule in self.rule_registry.get_all_rules():
                    rule_violations = rule.evaluate(node, context)
                    violations.extend(rule_violations)
                
                # Calculate score
                function_score = self.score_calculator.calculate_function_score(
                    node.name, node.lineno, violations
                )
                
                function_scores.append(function_score)
        
        return function_scores
    
    def _analyze_classes(self, tree: ast.AST, context: Any) -> List[ClassScore]:
        """
        Analyze all classes in the AST.
        
        Args:
            tree: The AST to analyze
            context: Analysis context
            
        Returns:
            List of ClassScore objects
        """
        class_scores = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Find constructor (__init__) method
                constructor_violations = []
                method_scores = []
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        # Evaluate constructor rules
                        for rule in self.rule_registry.get_all_rules():
                            rule_violations = rule.evaluate(item, context)
                            constructor_violations.extend(rule_violations)
                    elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Evaluate method rules
                        violations = []
                        for rule in self.rule_registry.get_all_rules():
                            rule_violations = rule.evaluate(item, context)
                            violations.extend(rule_violations)
                        
                        method_score = self.score_calculator.calculate_function_score(
                            item.name, item.lineno, violations
                        )
                        method_scores.append(method_score)
                
                class_score = ClassScore(
                    name=node.name,
                    line_number=node.lineno,
                    constructor_violations=constructor_violations,
                    method_scores=method_scores
                )
                
                class_scores.append(class_score)
        
        return class_scores
