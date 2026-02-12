"""
Report generation accuracy and formatting tests.

Tests that both text and JSON formatters produce accurate and well-formatted output.
"""

import pytest
import json
from testability_analyzer.formatters.text_formatter import TextFormatter
from testability_analyzer.formatters.json_formatter import JSONFormatter
from testability_analyzer.base import FileScore, FunctionScore, ClassScore, Violation


class TestReportGeneration:
    """Test cases for report generation accuracy and formatting."""
    
    def setup_method(self):
        self.text_formatter = TextFormatter(verbose=False)
        self.text_formatter_verbose = TextFormatter(verbose=True)
        self.json_formatter = JSONFormatter(verbose=False)
        self.json_formatter_verbose = JSONFormatter(verbose=True)
        
        # Create sample data for testing
        self.sample_file_score = self._create_sample_file_score()
    
    def _create_sample_file_score(self) -> FileScore:
        """Create a sample FileScore for testing."""
        # Create sample violations
        violations = [
            Violation(
                rule_name="External Dependency Count",
                description="External dependency: File System",
                points_deducted=5,
                line_number=10,
                function_name="test_function",
                is_red_flag=False
            ),
            Violation(
                rule_name="Non-Deterministic Time Usage",
                description="Non-deterministic time usage makes testing difficult",
                points_deducted=10,
                line_number=15,
                function_name="test_function",
                is_red_flag=True
            )
        ]
        
        # Create sample function score
        function_score = FunctionScore(
            name="test_function",
            line_number=5,
            baseline_score=100,
            final_score=85,  # 100 - 5 - 10
            violations=violations
        )
        
        # Create sample class score
        class_score = ClassScore(
            name="TestClass",
            line_number=20,
            constructor_violations=[
                Violation(
                    rule_name="Constructor Side Effects",
                    description="Constructor has side effects",
                    points_deducted=15,
                    line_number=21,
                    function_name="TestClass.__init__",
                    is_red_flag=True
                )
            ],
            method_scores=[function_score]
        )
        
        return FileScore(
            file_path="/test/sample.py",
            overall_score=70,  # Worst score (85 vs 70 from constructor)
            classification="High Friction",
            function_scores=[function_score],
            class_scores=[class_score],
            red_flags=[v for v in violations if v.is_red_flag] + class_score.constructor_violations
        )
    
    def test_text_formatter_basic_structure(self):
        """Test text formatter basic structure."""
        output = self.text_formatter.format([self.sample_file_score])
        
        # Check for required sections
        assert "Testability Analysis Report" in output
        assert "Summary:" in output
        assert "/test/sample.py" in output
        assert "Score:" in output
        assert "Classification:" in output
        
        # Check for score and classification
        assert "70" in output
        assert "High Friction" in output
    
    def test_text_formatter_red_flags(self):
        """Test text formatter red flag prominence."""
        output = self.text_formatter.format([self.sample_file_score])
        
        # Check for red flags section
        assert "🚨 RED FLAGS:" in output
        assert "Non-Deterministic Time Usage" in output
        assert "Constructor Side Effects" in output
    
    def test_text_formatter_verbose_mode(self):
        """Test text formatter verbose mode shows more details."""
        output_verbose = self.text_formatter_verbose.format([self.sample_file_score])
        output_normal = self.text_formatter.format([self.sample_file_score])
        
        # Verbose output should be longer
        assert len(output_verbose) > len(output_normal)
        
        # Should show function violations in verbose mode
        assert "External Dependency Count" in output_verbose
        assert "line 10" in output_verbose
        assert "[-5 points]" in output_verbose
    
    def test_text_formatter_color_coding(self):
        """Test text formatter color coding."""
        output = self.text_formatter.format([self.sample_file_score])
        
        # Check for color codes (should be present)
        assert '\033[' in output  # ANSI color codes
        
        # Check for different colors based on score
        assert '\033[91m' in output or '\033[93m' in output  # Red or yellow for 70 score
    
    def test_json_formatter_valid_json(self):
        """Test JSON formatter produces valid JSON."""
        output = self.json_formatter.format([self.sample_file_score])
        
        # Should be valid JSON
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
        
        # Check required top-level keys
        assert 'metadata' in data
        assert 'summary' in data
        assert 'files' in data
    
    def test_json_formatter_metadata(self):
        """Test JSON formatter metadata section."""
        output = self.json_formatter.format([self.sample_file_score])
        data = json.loads(output)
        
        metadata = data['metadata']
        assert 'tool' in metadata
        assert 'version' in metadata
        assert 'timestamp' in metadata
        assert 'format_version' in metadata
        
        assert metadata['tool'] == 'Testability Analyzer'
        assert metadata['version'] == '0.1.0'
    
    def test_json_formatter_summary(self):
        """Test JSON formatter summary section."""
        output = self.json_formatter.format([self.sample_file_score])
        data = json.loads(output)
        
        summary = data['summary']
        assert 'total_files' in summary
        assert 'total_functions' in summary
        assert 'total_classes' in summary
        assert 'total_violations' in summary
        assert 'total_red_flags' in summary
        assert 'score_statistics' in summary
        assert 'classifications' in summary
        
        # Check values
        assert summary['total_files'] == 1
        assert summary['total_functions'] == 1
        assert summary['total_classes'] == 1
        assert summary['total_violations'] == 3
        assert summary['total_red_flags'] == 2
    
    def test_json_formatter_file_details(self):
        """Test JSON formatter file details."""
        output = self.json_formatter.format([self.sample_file_score])
        data = json.loads(output)
        
        files = data['files']
        assert len(files) == 1
        
        file_data = files[0]
        assert 'path' in file_data
        assert 'overall_score' in file_data
        assert 'classification' in file_data
        assert 'red_flags' in file_data
        assert 'functions' in file_data
        assert 'classes' in file_data
        
        # Check values
        assert file_data['path'] == '/test/sample.py'
        assert file_data['overall_score'] == 70
        assert file_data['classification'] == 'High Friction'
        assert len(file_data['red_flags']) == 2
    
    def test_json_formatter_violation_details(self):
        """Test JSON formatter violation details."""
        output = self.json_formatter.format([self.sample_file_score])
        data = json.loads(output)
        
        file_data = data['files'][0]
        
        # Check function violations
        functions = file_data['functions']
        assert len(functions) == 1
        
        func_data = functions[0]
        assert 'name' in func_data
        assert 'line_number' in func_data
        assert 'baseline_score' in func_data
        assert 'final_score' in func_data
        assert 'violations' in func_data
        
        # Check violation structure
        violations = func_data['violations']
        assert len(violations) == 2
        
        for violation in violations:
            assert 'rule_name' in violation
            assert 'description' in violation
            assert 'points_deducted' in violation
            assert 'line_number' in violation
            assert 'function_name' in violation
            assert 'is_red_flag' in violation
    
    def test_json_formatter_verbose_mode(self):
        """Test JSON formatter verbose mode includes score breakdown."""
        output_normal = self.json_formatter.format([self.sample_file_score])
        output_verbose = self.json_formatter_verbose.format([self.sample_file_score])
        
        data_normal = json.loads(output_normal)
        data_verbose = json.loads(output_verbose)
        
        # Verbose mode should include score breakdown
        file_data_verbose = data_verbose['files'][0]
        assert 'score_breakdown' in file_data_verbose
        
        # Normal mode should not include score breakdown
        file_data_normal = data_normal['files'][0]
        assert 'score_breakdown' not in file_data_normal
    
    def test_json_formatter_score_breakdown(self):
        """Test JSON formatter score breakdown in verbose mode."""
        output = self.json_formatter_verbose.format([self.sample_file_score])
        data = json.loads(output)
        
        file_data = data['files'][0]
        breakdown = file_data['score_breakdown']
        
        assert 'baseline_score' in breakdown
        assert 'total_deductions' in breakdown
        assert 'violations_by_rule' in breakdown
        assert 'red_flag_count' in breakdown
        assert 'final_score' in breakdown
        
        # Check values
        assert breakdown['baseline_score'] == 100
        assert breakdown['total_deductions'] == 30
        assert breakdown['red_flag_count'] == 2
        assert breakdown['final_score'] == 70
    
    def test_multiple_files_formatting(self):
        """Test formatting of multiple files."""
        # Create second sample file
        sample_file2 = FileScore(
            file_path="/test/sample2.py",
            overall_score=95,
            classification="Healthy",
            function_scores=[],
            class_scores=[],
            red_flags=[]
        )
        
        # Test text formatter
        output = self.text_formatter.format([self.sample_file_score, sample_file2])
        assert "/test/sample.py" in output
        assert "/test/sample2.py" in output
        
        # Test JSON formatter
        output = self.json_formatter.format([self.sample_file_score, sample_file2])
        data = json.loads(output)
        assert len(data['files']) == 2
        assert data['summary']['total_files'] == 2
    
    def test_empty_file_list(self):
        """Test formatting with empty file list."""
        # Test text formatter
        output = self.text_formatter.format([])
        assert "Testability Analysis Report" in output
        assert "Summary:" in output
        assert "Files analyzed: 0" in output
        
        # Test JSON formatter
        output = self.json_formatter.format([])
        data = json.loads(output)
        assert data['summary']['total_files'] == 0
        assert len(data['files']) == 0
    
    def test_score_color_mapping(self):
        """Test that scores are colored correctly."""
        # Test different score ranges
        test_cases = [
            (90, 'green'),    # Healthy
            (70, 'yellow'),   # Caution
            (50, 'magenta'),  # High Friction
            (20, 'red')       # Refactor First
        ]
        
        for score, expected_color in test_cases:
            file_score = FileScore(
                file_path="/test.py",
                overall_score=score,
                classification=self.text_formatter._get_score_color(score),
                function_scores=[],
                class_scores=[],
                red_flags=[]
            )
            
            output = self.text_formatter.format([file_score])
            color_code = self.text_formatter.colors[expected_color]
            assert color_code in output
