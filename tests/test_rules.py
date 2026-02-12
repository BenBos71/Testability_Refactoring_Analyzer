"""
Unit tests for all testability rules.

Comprehensive test coverage for all 12 rule implementations with various scenarios.
"""

import pytest
import ast
from testability_analyzer.rules import (
    ExternalDependencyRule, FileIORule, TimeUsageRule, RandomnessRule,
    GlobalStateRule, MixedIOLogicRule, BranchExplosionRule,
    ExceptionControlFlowRule, ConstructorSideEffectsRule, HiddenImportsRule,
    ParameterCountRule, ObservabilityRule
)
from testability_analyzer.ast_utils import AnalysisContext


class TestExternalDependencyRule:
    """Test cases for External Dependency Count rule."""
    
    def setup_method(self):
        self.rule = ExternalDependencyRule()
        self.context = AnalysisContext()
    
    def test_no_external_dependencies(self):
        """Test function with no external dependencies."""
        code = """
def calculate_sum(a, b):
    return a + b
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_file_system_dependency(self):
        """Test function with file system dependency."""
        code = """
def read_config():
    with open('config.json', 'r') as f:
        return json.load(f)
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 5
        assert "File System" in violations[0].description
    
    def test_network_dependency(self):
        """Test function with network dependency."""
        code = """
def fetch_data(url):
    return requests.get(url).json()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 5


class TestFileIORule:
    """Test cases for Direct File I/O in Logic rule."""
    
    def setup_method(self):
        self.rule = FileIORule()
        self.context = AnalysisContext()
    
    def test_pure_logic_function(self):
        """Test pure logic function."""
        code = """
def calculate_area(length, width):
    return length * width
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_io_function_name(self):
        """Test function with IO-related name (should be skipped)."""
        code = """
def read_file_content():
    with open('file.txt', 'r') as f:
        return f.read()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_mixed_io_and_logic(self):
        """Test function mixing I/O and logic."""
        code = """
def process_data():
    with open('data.txt', 'r') as f:
        data = f.read()
    return data.upper()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 10


class TestTimeUsageRule:
    """Test cases for Non-Deterministic Time Usage rule."""
    
    def setup_method(self):
        self.rule = TimeUsageRule()
        self.context = AnalysisContext()
    
    def test_no_time_usage(self):
        """Test function without time usage."""
        code = """
def add_numbers(a, b):
    return a + b
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_time_function_usage(self):
        """Test function using time.time()."""
        code = """
def get_timestamp():
    return time.time()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 10
        assert violations[0].is_red_flag == True
    
    def test_datetime_usage(self):
        """Test function using datetime.now()."""
        code = """
def get_current_time():
    return datetime.now()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 10


class TestRandomnessRule:
    """Test cases for Randomness Usage rule."""
    
    def setup_method(self):
        self.rule = RandomnessRule()
        self.context = AnalysisContext()
    
    def test_no_randomness(self):
        """Test function without randomness."""
        code = """
def calculate_sum(a, b):
    return a + b
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_random_usage(self):
        """Test function using random.random()."""
        code = """
def get_random_value():
    return random.random()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 10
        assert violations[0].is_red_flag == True
    
    def test_uuid_usage(self):
        """Test function using uuid.uuid4()."""
        code = """
def generate_id():
    return uuid.uuid4()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1


class TestGlobalStateRule:
    """Test cases for Global State Mutation rule."""
    
    def setup_method(self):
        self.rule = GlobalStateRule()
        self.context = AnalysisContext()
        self.context.global_variables = {'global_counter', 'config'}
    
    def test_no_global_mutation(self):
        """Test function without global state mutation."""
        code = """
def calculate_sum(a, b):
    return a + b
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_global_declaration(self):
        """Test function with global declaration."""
        code = """
def increment_counter():
    global global_counter
    global_counter += 1
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 10
        assert violations[0].is_red_flag == True


class TestMixedIOLogicRule:
    """Test cases for Mixed I/O and Logic rule."""
    
    def setup_method(self):
        self.rule = MixedIOLogicRule()
        self.context = AnalysisContext()
    
    def test_pure_io_function(self):
        """Test pure I/O function."""
        code = """
def read_file_content():
    with open('file.txt', 'r') as f:
        return f.read()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_pure_logic_function(self):
        """Test pure logic function."""
        code = """
def calculate_sum(a, b):
    return a + b
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_mixed_io_and_logic(self):
        """Test function mixing I/O and logic."""
        code = """
def process_and_save():
    data = calculate_complex_logic()
    with open('output.txt', 'w') as f:
        f.write(data)
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 8


class TestBranchExplosionRule:
    """Test cases for Branch Explosion Risk rule."""
    
    def setup_method(self):
        self.rule = BranchExplosionRule()
        self.context = AnalysisContext()
    
    def test_simple_function(self):
        """Test function with minimal branching."""
        code = """
def simple_function(x):
    if x > 0:
        return x
    return 0
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_complex_branching(self):
        """Test function with excessive branching."""
        code = """
def complex_function(x, y, z, a, b):
    if x > 0:
        if y > 0:
            if z > 0:
                if a > 0:
                    if b > 0:
                        return x + y + z + a + b
    return 0
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 4  # 5 branches - 3 threshold = 2 * 2 points


class TestExceptionControlFlowRule:
    """Test cases for Exception-Driven Control Flow rule."""
    
    def setup_method(self):
        self.rule = ExceptionControlFlowRule()
        self.context = AnalysisContext()
    
    def test_normal_exception_handling(self):
        """Test normal exception handling."""
        code = """
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 0
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_exception_as_control_flow(self):
        """Test exception used for control flow."""
        code = """
def process_list(items):
    try:
        while True:
            item = items.pop()
            process(item)
    except IndexError:
        pass
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 5


class TestConstructorSideEffectsRule:
    """Test cases for Constructor Side Effects rule."""
    
    def setup_method(self):
        self.rule = ConstructorSideEffectsRule()
        self.context = AnalysisContext()
    
    def test_clean_constructor(self):
        """Test constructor without side effects."""
        code = """
class MyClass:
    def __init__(self, value):
        self.value = value
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_constructor_with_side_effects(self):
        """Test constructor with side effects."""
        code = """
class MyClass:
    def __init__(self):
        with open('config.txt', 'r') as f:
            self.config = f.read()
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 15


class TestHiddenImportsRule:
    """Test cases for Hidden Dependencies via Imports-in-Function rule."""
    
    def setup_method(self):
        self.rule = HiddenImportsRule()
        self.context = AnalysisContext()
    
    def test_no_hidden_imports(self):
        """Test function without hidden imports."""
        code = """
def calculate_sum(a, b):
    return a + b
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_hidden_import(self):
        """Test function with hidden import."""
        code = """
def process_data():
    import requests
    return requests.get('http://example.com')
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 5


class TestParameterCountRule:
    """Test cases for Excessive Parameter Count rule."""
    
    def setup_method(self):
        self.rule = ParameterCountRule()
        self.context = AnalysisContext()
    
    def test_few_parameters(self):
        """Test function with few parameters."""
        code = """
def simple_func(a, b, c):
    return a + b + c
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_excessive_parameters(self):
        """Test function with excessive parameters."""
        code = """
def complex_func(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 5


class TestObservabilityRule:
    """Test cases for Low Observability rule."""
    
    def setup_method(self):
        self.rule = ObservabilityRule()
        self.context = AnalysisContext()
    
    def test_observable_function(self):
        """Test function with good observability."""
        code = """
def calculate_and_log(a, b):
    result = a + b
    logging.info(f"Calculated: {result}")
    return result
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 0
    
    def test_unobservable_function(self):
        """Test function with low observability."""
        code = """
def silent_function(a, b):
    result = a + b
    # No return, no logging, no assertions
"""
        tree = ast.parse(code)
        violations = self.rule.evaluate(tree.body[0], self.context)
        assert len(violations) == 1
        assert violations[0].points_deducted == 5
