"""
Scoring system for testability analysis.

Provides algorithms for calculating testability scores based on rule violations
and aggregating scores at different levels (function, class, file).
"""

from typing import List, Dict, Any
from ..base import FunctionScore, ClassScore, Violation


class ScoreCalculator:
    """Calculates testability scores based on rule violations."""
    
    def __init__(self):
        self.baseline_score = 100
        self.min_score = 0
    
    def calculate_function_score(self, function_name: str, line_number: int, violations: List[Violation]) -> FunctionScore:
        """
        Calculate testability score for a single function.
        
        Args:
            function_name: Name of the function
            line_number: Line number where function starts
            violations: List of violations found in the function
            
        Returns:
            FunctionScore with calculated score and violations
        """
        # Start with baseline score
        score = self.baseline_score
        
        # Subtract penalty points for each violation
        total_deduction = sum(violation.points_deducted for violation in violations)
        score -= total_deduction
        
        # Ensure score doesn't go below minimum
        score = max(score, self.min_score)
        
        return FunctionScore(
            name=function_name,
            line_number=line_number,
            baseline_score=self.baseline_score,
            final_score=score,
            violations=violations
        )
    
    def calculate_class_score(self, class_name: str, line_number: int, 
                           constructor_violations: List[Violation], 
                           method_scores: List[FunctionScore]) -> ClassScore:
        """
        Calculate testability score for a class.
        
        Args:
            class_name: Name of the class
            line_number: Line number where class starts
            constructor_violations: Violations found in constructor
            method_scores: Scores for all methods in the class
            
        Returns:
            ClassScore with calculated scores
        """
        return ClassScore(
            name=class_name,
            line_number=line_number,
            constructor_violations=constructor_violations,
            method_scores=method_scores
        )
    
    def aggregate_file_score(self, function_scores: List[FunctionScore], 
                          class_scores: List[ClassScore]) -> int:
        """
        Aggregate scores for an entire file.
        
        Args:
            function_scores: Scores for all functions in the file
            class_scores: Scores for all classes in the file
            
        Returns:
            Overall file score
        """
        all_scores = []
        
        # Add function scores
        all_scores.extend([score.final_score for score in function_scores])
        
        # Add method scores from classes
        for class_score in class_scores:
            all_scores.extend([method.final_score for method in class_score.method_scores])
        
        # Add constructor penalties
        for class_score in class_scores:
            constructor_penalty = sum(v.points_deducted for v in class_score.constructor_violations)
            if constructor_penalty > 0:
                # Constructor score is baseline minus penalties
                constructor_score = max(self.baseline_score - constructor_penalty, self.min_score)
                all_scores.append(constructor_score)
        
        if not all_scores:
            return self.baseline_score  # Empty file gets perfect score
        
        # Use worst score as file score (conservative approach)
        return min(all_scores)
    
    def get_score_breakdown(self, violations: List[Violation]) -> Dict[str, Any]:
        """
        Get detailed breakdown of score deductions.
        
        Args:
            violations: List of violations to analyze
            
        Returns:
            Dictionary with detailed breakdown
        """
        breakdown = {
            'baseline_score': self.baseline_score,
            'total_deductions': 0,
            'violations_by_rule': {},
            'red_flag_count': 0,
            'final_score': self.baseline_score
        }
        
        # Group violations by rule
        for violation in violations:
            rule_name = violation.rule_name
            if rule_name not in breakdown['violations_by_rule']:
                breakdown['violations_by_rule'][rule_name] = {
                    'count': 0,
                    'total_points': 0,
                    'violations': []
                }
            
            breakdown['violations_by_rule'][rule_name]['count'] += 1
            breakdown['violations_by_rule'][rule_name]['total_points'] += violation.points_deducted
            breakdown['violations_by_rule'][rule_name]['violations'].append({
                'line': violation.line_number,
                'function': violation.function_name,
                'description': violation.description,
                'points': violation.points_deducted
            })
            
            if violation.is_red_flag:
                breakdown['red_flag_count'] += 1
        
        # Calculate total deductions
        breakdown['total_deductions'] = sum(v.points_deducted for v in violations)
        breakdown['final_score'] = max(self.baseline_score - breakdown['total_deductions'], self.min_score)
        
        return breakdown
