"""
Human-readable text report formatter.

Provides formatted text output with color coding and clear structure
for displaying testability analysis results.
"""

from typing import List, Dict, Any
from ..base import FileScore, FunctionScore, ClassScore, Violation


class TextFormatter:
    """Formats analysis results as human-readable text with color coding."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.colors = {
            'red': '\033[91m',
            'yellow': '\033[93m',
            'green': '\033[92m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
    
    def format(self, file_scores: List[FileScore]) -> str:
        """
        Format analysis results as text.
        
        Args:
            file_scores: List of file analysis results
            
        Returns:
            Formatted text string
        """
        output = []
        
        # Header
        output.append(self._format_header())
        
        # Summary
        output.append(self._format_summary(file_scores))
        
        # File details
        for file_score in file_scores:
            output.append(self._format_file(file_score))
        
        # Footer
        output.append(self._format_footer())
        
        return '\n\n'.join(output)
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text."""
        if color in self.colors:
            return f"{self.colors[color]}{text}{self.colors['end']}"
        return text
    
    def _format_header(self) -> str:
        """Format report header."""
        header = f"{self._colorize('Testability Analysis Report', 'bold')}"
        header += f"\n{'=' * 50}"
        return header
    
    def _format_summary(self, file_scores: List[FileScore]) -> str:
        """Format analysis summary."""
        total_files = len(file_scores)
        total_functions = sum(len(fs.function_scores) for fs in file_scores)
        total_classes = sum(len(fs.class_scores) for fs in file_scores)
        total_violations = sum(len(fs.function_scores) for fs in file_scores)
        
        # Calculate average score
        if file_scores:
            avg_score = sum(fs.overall_score for fs in file_scores) / len(file_scores)
        else:
            avg_score = 0
        
        summary = f"{self._colorize('Summary:', 'bold')}"
        summary += f"\nFiles analyzed: {total_files}"
        summary += f"\nFunctions analyzed: {total_functions}"
        summary += f"\nClasses analyzed: {total_classes}"
        summary += f"\nAverage score: {avg_score:.1f}"
        
        return summary
    
    def _format_file(self, file_score: FileScore) -> str:
        """Format individual file results."""
        output = []
        
        # File header with score
        score_color = self._get_score_color(file_score.overall_score)
        file_header = f"\n{self._colorize('📁 ' + file_score.file_path, 'blue')}"
        file_header += f"\nScore: {self._colorize(str(file_score.overall_score), score_color)}"
        file_header += f" | Classification: {self._colorize(file_score.classification, score_color)}"
        output.append(file_header)
        
        # Red flags (prominent)
        if file_score.red_flags:
            output.append(self._format_red_flags(file_score.red_flags))
        
        # Function scores
        if file_score.function_scores:
            output.append(self._format_functions(file_score.function_scores))
        
        # Class scores
        if file_score.class_scores:
            output.append(self._format_classes(file_score.class_scores))
        
        return '\n'.join(output)
    
    def _format_red_flags(self, red_flags: List[Violation]) -> str:
        """Format red flag violations with prominence."""
        output = []
        output.append(f"\n{self._colorize('🚨 RED FLAGS:', 'red')}")
        
        for flag in red_flags:
            flag_text = f"  {self._colorize('•', 'red')} {flag.rule_name}"
            flag_text += f" (line {flag.line_number})"
            flag_text += f" - {flag.description}"
            flag_text += f" [-{flag.points_deducted} points]"
            output.append(flag_text)
        
        return '\n'.join(output)
    
    def _format_functions(self, function_scores: List[FunctionScore]) -> str:
        """Format function scores and violations."""
        output = []
        output.append(f"\n{self._colorize('Functions:', 'cyan')}")
        
        for func_score in function_scores:
            score_color = self._get_score_color(func_score.final_score)
            func_text = f"  {func_score.name}(): {self._colorize(str(func_score.final_score), score_color)}"
            
            if self.verbose and func_score.violations:
                func_text += self._format_function_violations(func_score.violations)
            
            output.append(func_text)
        
        return '\n'.join(output)
    
    def _format_function_violations(self, violations: List[Violation]) -> str:
        """Format function violations."""
        output = []
        for violation in violations:
            if violation.is_red_flag:
                continue  # Already shown in red flags section
            
            violation_text = f"\n    {self._colorize('•', 'yellow')} {violation.rule_name}"
            violation_text += f" (line {violation.line_number})"
            violation_text += f" - {violation.description}"
            violation_text += f" [-{violation.points_deducted} points]"
            output.append(violation_text)
        
        return '\n'.join(output)
    
    def _format_classes(self, class_scores: List[ClassScore]) -> str:
        """Format class scores and violations."""
        output = []
        output.append(f"\n{self._colorize('Classes:', 'magenta')}")
        
        for class_score in class_scores:
            # Constructor violations
            if class_score.constructor_violations:
                output.append(f"  {class_score.name} (constructor):")
                for violation in class_score.constructor_violations:
                    violation_text = f"    {self._colorize('•', 'red')} {violation.rule_name}"
                    violation_text += f" - {violation.description}"
                    violation_text += f" [-{violation.points_deducted} points]"
                    output.append(violation_text)
            
            # Method scores
            if class_score.method_scores:
                for method_score in class_score.method_scores:
                    score_color = self._get_score_color(method_score.final_score)
                    method_text = f"  {class_score.name}.{method_score.name}(): {self._colorize(str(method_score.final_score), score_color)}"
                    
                    if self.verbose and method_score.violations:
                        method_text += self._format_function_violations(method_score.violations)
                    
                    output.append(method_text)
        
        return '\n'.join(output)
    
    def _format_footer(self) -> str:
        """Format report footer."""
        footer = f"\n{self._colorize('Report generated by Testability Analyzer', 'cyan')}"
        footer += f"\n{self._colorize('For detailed refactoring suggestions, run with --verbose', 'white')}"
        return footer
    
    def _get_score_color(self, score: int) -> str:
        """Get color based on score."""
        if score >= 80:
            return 'green'
        elif score >= 60:
            return 'yellow'
        elif score >= 40:
            return 'magenta'
        else:
            return 'red'
