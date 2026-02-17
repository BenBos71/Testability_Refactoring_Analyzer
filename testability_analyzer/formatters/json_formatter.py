"""
Machine-readable JSON report formatter.

Provides JSON output suitable for CI/CD integration and automated processing.
"""

import json
from typing import List, Dict, Any
from datetime import datetime
from ..base import FileScore, FunctionScore, ClassScore, Violation


class JSONFormatter:
    """Formats analysis results as machine-readable JSON."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def format(self, file_scores: List[FileScore]) -> str:
        """
        Format analysis results as JSON.
        
        Args:
            file_scores: List of file analysis results
            
        Returns:
            JSON string
        """
        report = {
            'metadata': self._create_metadata(),
            'summary': self._create_summary(file_scores),
            'files': [self._format_file(fs) for fs in file_scores]
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def _create_metadata(self) -> Dict[str, Any]:
        """Create report metadata."""
        return {
            'tool': 'Testability Analyzer',
            'version': '0.1.0',
            'timestamp': datetime.now().isoformat(),
            'format_version': '1.0'
        }
    
    def _create_summary(self, file_scores: List[FileScore]) -> Dict[str, Any]:
        """Create analysis summary."""
        total_files = len(file_scores)
        total_functions = sum(len(fs.function_scores) for fs in file_scores)
        total_classes = sum(len(fs.class_scores) for fs in file_scores)
        total_violations = 0
        total_red_flags = 0
        
        # Count violations and red flags.
        # Treat file_score.function_scores as the authoritative list of scored functions.
        # Do not double-count method_scores here.
        for fs in file_scores:
            for func_score in fs.function_scores:
                total_violations += len(func_score.violations)
                total_red_flags += sum(1 for v in func_score.violations if v.is_red_flag)

            for class_score in fs.class_scores:
                total_violations += len(class_score.constructor_violations)
                total_red_flags += sum(1 for v in class_score.constructor_violations if v.is_red_flag)
        
        # Calculate score statistics
        if file_scores:
            scores = [fs.overall_score for fs in file_scores]
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
        else:
            avg_score = min_score = max_score = 0
        
        # Classify files
        classifications = {}
        for fs in file_scores:
            classification = fs.classification
            classifications[classification] = classifications.get(classification, 0) + 1
        
        return {
            'total_files': total_files,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'total_violations': total_violations,
            'total_red_flags': total_red_flags,
            'score_statistics': {
                'average': round(avg_score, 1),
                'minimum': min_score,
                'maximum': max_score
            },
            'classifications': classifications
        }
    
    def _format_file(self, file_score: FileScore) -> Dict[str, Any]:
        """Format individual file results."""
        file_data = {
            'path': file_score.file_path,
            'overall_score': file_score.overall_score,
            'classification': file_score.classification,
            'red_flags': [self._format_violation(v) for v in file_score.red_flags],
            'functions': [self._format_function(f) for f in file_score.function_scores],
            'classes': [self._format_class(c) for c in file_score.class_scores]
        }
        
        # Add score breakdown if verbose
        if self.verbose:
            all_violations = []
            for func_score in file_score.function_scores:
                all_violations.extend(func_score.violations)
            for class_score in file_score.class_scores:
                all_violations.extend(class_score.constructor_violations)

            file_data['score_breakdown'] = self._create_score_breakdown(
                violations=all_violations,
                final_score=file_score.overall_score,
            )
        
        return file_data
    
    def _format_function(self, func_score: FunctionScore) -> Dict[str, Any]:
        """Format function score and violations."""
        function_data = {
            'name': func_score.name,
            'line_number': func_score.line_number,
            'baseline_score': func_score.baseline_score,
            'final_score': func_score.final_score,
            'violations': [self._format_violation(v) for v in func_score.violations]
        }
        
        # Add classification if verbose
        if self.verbose:
            # Classify function score
            if func_score.final_score >= 75:
                classification = 'Easy'
            elif func_score.final_score >= 55:
                classification = 'Testable'
            elif func_score.final_score >= 35:
                classification = 'Hard'
            else:
                classification = 'Painful'
            
            function_data['classification'] = classification
        
        return function_data
    
    def _format_class(self, class_score: ClassScore) -> Dict[str, Any]:
        """Format class score and violations."""
        class_data = {
            'name': class_score.name,
            'line_number': class_score.line_number,
            'constructor_violations': [self._format_violation(v) for v in class_score.constructor_violations],
            'methods': [self._format_function(m) for m in class_score.method_scores]
        }
        
        # Calculate constructor score if there are violations
        if class_score.constructor_violations:
            constructor_penalty = sum(v.points_deducted for v in class_score.constructor_violations)
            constructor_score = max(100 - constructor_penalty, 0)
            class_data['constructor_score'] = constructor_score
        
        return class_data
    
    def _format_violation(self, violation: Violation) -> Dict[str, Any]:
        """Format individual violation."""
        return {
            'rule_name': violation.rule_name,
            'description': violation.description,
            'points_deducted': violation.points_deducted,
            'line_number': violation.line_number,
            'function_name': violation.function_name,
            'is_red_flag': violation.is_red_flag
        }
    
    def _create_score_breakdown(self, violations: List[Violation], final_score: int) -> Dict[str, Any]:
        """Create detailed score breakdown."""
        breakdown = {
            'baseline_score': 100,
            'total_deductions': 0,
            'violations_by_rule': {},
            'red_flag_count': 0,
            'final_score': final_score
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
        
        # Calculate totals based on the actual final score for the file.
        breakdown['total_deductions'] = max(100 - final_score, 0)
        
        return breakdown
