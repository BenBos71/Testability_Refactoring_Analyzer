"""
Integration tests with sample codebases.

Tests the complete analysis pipeline on realistic code examples
of varying complexity levels.
"""

import pytest
import tempfile
import os
from pathlib import Path
from testability_analyzer.analyzer import TestabilityAnalyzer


class TestIntegration:
    """Integration tests for the complete analyzer pipeline."""
    
    def setup_method(self):
        self.analyzer = TestabilityAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_file(self, filename: str, content: str) -> str:
        """Create a test file with given content."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_simple_codebase(self):
        """Test analysis of simple, well-structured code."""
        simple_code = '''
def calculate_area(length, width):
    """Calculate rectangle area."""
    return length * width

def format_result(area):
    """Format the result for display."""
    return f"Area: {area:.2f}"

class Rectangle:
    """Simple rectangle class."""
    
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    def area(self):
        return calculate_area(self.length, self.width)
'''
        filepath = self._create_test_file('simple.py', simple_code)
        result = self.analyzer.analyze_file(filepath)
        
        assert result.overall_score >= 80  # Should be Healthy
        assert result.classification == 'Healthy'
        assert len(result.red_flags) == 0
        assert len(result.function_scores) == 2
        assert len(result.class_scores) == 1
    
    def test_medium_complexity_codebase(self):
        """Test analysis of medium complexity code."""
        medium_code = '''
import json
import os

def load_config(config_path):
    """Load configuration from file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def process_data(data, threshold=10):
    """Process data with some branching."""
    results = []
    for item in data:
        if item > threshold:
            results.append(item * 2)
        elif item > 5:
            results.append(item * 1.5)
        else:
            results.append(item)
    return results

class DataProcessor:
    """Data processing class with some issues."""
    
    def __init__(self, config_file):
        self.config = load_config(config_file)
        self.processed_count = 0
    
    def process_items(self, items):
        """Process multiple items."""
        for item in items:
            self.processed_count += 1
            yield process_data(item, self.config.get('threshold', 10))
'''
        filepath = self._create_test_file('medium.py', medium_code)
        result = self.analyzer.analyze_file(filepath)
        
        assert 40 <= result.overall_score < 80  # Should be Caution or High Friction
        assert result.classification in ['Caution', 'High Friction']
        assert len(result.function_scores) == 2
        assert len(result.class_scores) == 1
    
    def test_high_complexity_codebase(self):
        """Test analysis of high complexity code with many issues."""
        complex_code = '''
import time
import random
import requests
import json
import os
from datetime import datetime

def complex_function(param1, param2, param3, param4, param5, param6, param7):
    """Function with many testability issues."""
    global global_state
    
    # Time dependency
    start_time = time.time()
    
    # Randomness
    random_value = random.random()
    
    # File I/O in logic
    with open('temp.txt', 'w') as f:
        f.write(str(random_value))
    
    # Complex branching
    if param1 > 0:
        if param2 > 0:
            if param3 > 0:
                if param4 > 0:
                    if param5 > 0:
                        result = param1 + param2 + param3 + param4 + param5
                    else:
                        result = param1 + param2 + param3 + param4
                else:
                    result = param1 + param2 + param3
            else:
                result = param1 + param2
        else:
            result = param1
    else:
        result = 0
    
    # Exception-driven control flow
    try:
        data = requests.get('http://example.com/api').json()
    except:
        data = {}
    
    global_state = result
    return result

class ProblematicClass:
    """Class with constructor side effects."""
    
    def __init__(self, config_path):
        # Side effect in constructor
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Hidden import
        import uuid
        self.id = uuid.uuid4()
        
        # Global state mutation
        global global_counter
        global_counter = 0
    
    def complex_method(self, a, b, c, d, e, f):
        """Method with many parameters and no return."""
        # No observability
        temp = a + b + c + d + e + f
        # No return, no logging
        
    def method_with_hidden_import(self):
        """Method with hidden import."""
        import numpy as np
        return np.array([1, 2, 3])

global_state = 0
global_counter = 0
'''
        filepath = self._create_test_file('complex.py', complex_code)
        result = self.analyzer.analyze_file(filepath)
        
        assert result.overall_score < 40  # Should be Refactor First
        assert result.classification == 'Refactor First'
        assert len(result.red_flags) > 0
        assert len(result.function_scores) == 2
        assert len(result.class_scores) == 1
    
    def test_directory_analysis(self):
        """Test analysis of multiple files in directory."""
        # Create multiple test files
        simple_code = 'def add(a, b): return a + b'
        medium_code = '''
import json
def load_data():
    with open('data.json') as f:
        return json.load(f)
'''
        
        self._create_test_file('simple.py', simple_code)
        self._create_test_file('medium.py', medium_code)
        
        results = self.analyzer.analyze_directory(self.temp_dir)
        
        assert len(results) == 2
        assert any(r.file_path.endswith('simple.py') for r in results)
        assert any(r.file_path.endswith('medium.py') for r in results)
    
    def test_empty_file(self):
        """Test analysis of empty file."""
        filepath = self._create_test_file('empty.py', '')
        result = self.analyzer.analyze_file(filepath)
        
        assert result.overall_score == 100  # Empty file gets perfect score
        assert result.classification == 'Healthy'
        assert len(result.function_scores) == 0
        assert len(result.class_scores) == 0
    
    def test_syntax_error_file(self):
        """Test analysis of file with syntax error."""
        invalid_code = 'def broken_function(\n    # Missing closing parenthesis'
        filepath = self._create_test_file('invalid.py', invalid_code)
        result = self.analyzer.analyze_file(filepath)
        
        assert result.overall_score == 0  # Parse error gets 0 score
        assert result.classification == 'Parse Error'
    
    def test_score_calculation_accuracy(self):
        """Test that score calculations match expected values."""
        code_with_known_violations = '''
def function_with_violations():
    import requests  # Hidden import: -5 points
    with open('file.txt', 'r') as f:  # File I/O: -10 points
        data = f.read()
    return data.upper()
'''
        filepath = self._create_test_file('test_scores.py', code_with_known_violations)
        result = self.analyzer.analyze_file(filepath)
        
        # Should have baseline 100 - 5 (hidden import) - 10 (file I/O) = 85
        expected_score = 85
        assert result.overall_score == expected_score
        
        # Check individual violations
        function_score = result.function_scores[0]
        assert len(function_score.violations) == 2
        
        violation_points = sum(v.points_deducted for v in function_score.violations)
        assert violation_points == 15
