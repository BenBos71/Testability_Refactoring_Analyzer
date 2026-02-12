"""
CLI testing for various input scenarios and edge cases.

Tests the command-line interface with different arguments and edge cases.
"""

import pytest
import tempfile
import os
import subprocess
import sys
from pathlib import Path


class TestCLI:
    """Test cases for CLI functionality."""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.py')
        with open(self.test_file, 'w') as f:
            f.write('def test_func():\n    return 42\n')
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _run_cli(self, args):
        """Run CLI with given arguments and return result."""
        cli_path = os.path.join(os.path.dirname(__file__), '..', 'testability_analyzer', 'cli.py')
        cmd = [sys.executable, cli_path] + args
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
    
    def test_cli_help(self):
        """Test CLI help functionality."""
        returncode, stdout, stderr = self._run_cli(['--help'])
        assert returncode == 0
        assert 'Testability Analyzer' in stdout
        assert 'usage:' in stdout
    
    def test_cli_version(self):
        """Test CLI version functionality."""
        returncode, stdout, stderr = self._run_cli(['--version'])
        assert returncode == 0
        assert '0.1.0' in stdout
    
    def test_single_file_analysis(self):
        """Test analysis of single file."""
        returncode, stdout, stderr = self._run_cli([self.test_file])
        assert returncode == 0
        assert 'Testability Analysis Report' in stdout
        assert self.test_file in stdout
    
    def test_directory_analysis(self):
        """Test analysis of directory."""
        returncode, stdout, stderr = self._run_cli([self.temp_dir])
        assert returncode == 0
        assert 'Testability Analysis Report' in stdout
    
    def test_json_output(self):
        """Test JSON output format."""
        returncode, stdout, stderr = self._run_cli([self.test_file, '--output', 'json'])
        assert returncode == 0
        # Check if output is valid JSON
        import json
        try:
            data = json.loads(stdout)
            assert 'metadata' in data
            assert 'files' in data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")
    
    def test_verbose_output(self):
        """Test verbose output."""
        returncode, stdout, stderr = self._run_cli([self.test_file, '--verbose'])
        assert returncode == 0
        assert 'Testability Analysis Report' in stdout
        # Verbose mode should show more details
        assert len(stdout) > 100  # Should be longer than normal output
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        nonexistent = os.path.join(self.temp_dir, 'nonexistent.py')
        returncode, stdout, stderr = self._run_cli([nonexistent])
        assert returncode != 0
        assert 'does not exist' in stderr
    
    def test_nonexistent_directory(self):
        """Test handling of nonexistent directory."""
        nonexistent = os.path.join(self.temp_dir, 'nonexistent_dir')
        returncode, stdout, stderr = self._run_cli([nonexistent])
        assert returncode != 0
        assert 'does not exist' in stderr
    
    def test_empty_directory(self):
        """Test analysis of empty directory."""
        empty_dir = os.path.join(self.temp_dir, 'empty')
        os.makedirs(empty_dir)
        
        returncode, stdout, stderr = self._run_cli([empty_dir])
        assert returncode == 0
        # Should handle empty directory gracefully
        assert 'Testability Analysis Report' in stdout
    
    def test_mixed_inputs(self):
        """Test analysis with mixed file and directory inputs."""
        # Create another test file
        test_file2 = os.path.join(self.temp_dir, 'test2.py')
        with open(test_file2, 'w') as f:
            f.write('def another_func():\n    return 24\n')
        
        returncode, stdout, stderr = self._run_cli([self.test_file, test_file2])
        assert returncode == 0
        assert 'Testability Analysis Report' in stdout
    
    def test_python_file_only(self):
        """Test that only Python files are analyzed."""
        # Create non-Python file
        non_python = os.path.join(self.temp_dir, 'test.txt')
        with open(non_python, 'w') as f:
            f.write('This is not Python code')
        
        returncode, stdout, stderr = self._run_cli([non_python])
        assert returncode != 0
        assert 'does not exist' in stderr or 'Warning: Skipping' in stderr
    
    def test_invalid_output_format(self):
        """Test invalid output format."""
        returncode, stdout, stderr = self._run_cli([self.test_file, '--output', 'invalid'])
        assert returncode != 0
        assert 'invalid choice' in stderr
    
    def test_file_with_syntax_error(self):
        """Test analysis of file with syntax error."""
        invalid_file = os.path.join(self.temp_dir, 'invalid.py')
        with open(invalid_file, 'w') as f:
            f.write('def invalid_function(\n    # Missing closing parenthesis')
        
        returncode, stdout, stderr = self._run_cli([invalid_file])
        assert returncode == 0  # Should not crash, but show parse error
        assert 'Testability Analysis Report' in stdout
    
    def test_large_file(self):
        """Test analysis of large file."""
        large_file = os.path.join(self.temp_dir, 'large.py')
        with open(large_file, 'w') as f:
            # Create a file with many functions
            for i in range(100):
                f.write(f'''
def function_{i}(param1, param2, param3, param4, param5, param6):
    """Function with many parameters and complexity."""
    if param1 > 0:
        if param2 > 0:
            if param3 > 0:
                if param4 > 0:
                    if param5 > 0:
                        return param1 + param2 + param3 + param4 + param5
    return 0
''')
        
        returncode, stdout, stderr = self._run_cli([large_file])
        assert returncode == 0
        assert 'Testability Analysis Report' in stdout
    
    def test_unicode_content(self):
        """Test analysis of file with Unicode content."""
        unicode_file = os.path.join(self.temp_dir, 'unicode.py')
        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write('def 测试函数():\n    """测试函数"""\n    return "测试结果"')
        
        returncode, stdout, stderr = self._run_cli([unicode_file])
        assert returncode == 0
        assert 'Testability Analysis Report' in stdout
    
    def test_no_arguments(self):
        """Test CLI with no arguments."""
        returncode, stdout, stderr = self._run_cli([])
        assert returncode != 0
        assert 'usage:' in stderr or 'required' in stderr
    
    def test_multiple_directories(self):
        """Test analysis of multiple directories."""
        dir1 = os.path.join(self.temp_dir, 'dir1')
        dir2 = os.path.join(self.temp_dir, 'dir2')
        os.makedirs(dir1)
        os.makedirs(dir2)
        
        # Add test files to each directory
        with open(os.path.join(dir1, 'test1.py'), 'w') as f:
            f.write('def func1(): return 1')
        with open(os.path.join(dir2, 'test2.py'), 'w') as f:
            f.write('def func2(): return 2')
        
        returncode, stdout, stderr = self._run_cli([dir1, dir2])
        assert returncode == 0
        assert 'Testability Analysis Report' in stdout
