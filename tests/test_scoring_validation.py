"""
Scoring calculation validation tests.

Validates that scoring calculations match the expected results from the project description.
"""

import pytest
from testability_analyzer.scoring import ScoreCalculator
from testability_analyzer.base import Violation


class TestScoringValidation:
    """Test cases to validate scoring calculations against project description."""
    
    def setup_method(self):
        self.calculator = ScoreCalculator()
    
    def test_baseline_score(self):
        """Test that baseline score is 100."""
        violations = []
        score = self.calculator.calculate_function_score("test_func", 1, violations)
        
        assert score.baseline_score == 100
        assert score.final_score == 100
    
    def test_single_violation_scoring(self):
        """Test scoring with single violations."""
        test_cases = [
            ("External Dependency Count", 5),
            ("Direct File I/O in Logic", 10),
            ("Non-Deterministic Time Usage", 10),
            ("Randomness Usage", 10),
            ("Global State Mutation", 10),
            ("Mixed I/O and Logic", 8),
            ("Exception-Driven Control Flow", 5),
            ("Constructor Side Effects", 15),
            ("Hidden Dependencies via Imports-in-Function", 5),
            ("Excessive Parameter Count", 5),
            ("Low Observability", 5),
        ]
        
        for rule_name, expected_points in test_cases:
            violations = [
                Violation(
                    rule_name=rule_name,
                    description="Test violation",
                    points_deducted=expected_points,
                    line_number=1,
                    function_name="test_func",
                    is_red_flag=False
                )
            ]
            
            score = self.calculator.calculate_function_score("test_func", 1, violations)
            expected_final = 100 - expected_points
            assert score.final_score == expected_final
    
    def test_multiple_violations_scoring(self):
        """Test scoring with multiple violations."""
        violations = [
            Violation(
                rule_name="External Dependency Count",
                description="File System dependency",
                points_deducted=5,
                line_number=1,
                function_name="test_func",
                is_red_flag=False
            ),
            Violation(
                rule_name="Direct File I/O in Logic",
                description="File operation in logic",
                points_deducted=10,
                line_number=2,
                function_name="test_func",
                is_red_flag=False
            ),
            Violation(
                rule_name="Non-Deterministic Time Usage",
                description="Time dependency",
                points_deducted=10,
                line_number=3,
                function_name="test_func",
                is_red_flag=True
            )
        ]
        
        score = self.calculator.calculate_function_score("test_func", 1, violations)
        expected_final = 100 - 5 - 10 - 10  # 75
        assert score.final_score == expected_final
    
    def test_score_never_below_zero(self):
        """Test that scores never go below 0."""
        # Create violations that would exceed 100 points
        violations = []
        for i in range(30):  # 30 violations * 5 points each = 150 points
            violations.append(
                Violation(
                    rule_name="External Dependency Count",
                    description=f"Violation {i}",
                    points_deducted=5,
                    line_number=i,
                    function_name="test_func",
                    is_red_flag=False
                )
            )
        
        score = self.calculator.calculate_function_score("test_func", 1, violations)
        assert score.final_score >= 0
        assert score.final_score == 0  # Should be exactly 0
    
    def test_branch_explosion_scoring(self):
        """Test branch explosion rule scoring."""
        # Test with 6 branches (3 over threshold, should be 6 points)
        violations = [
            Violation(
                rule_name="Branch Explosion Risk",
                description="Excessive branching: 6 branches (threshold: 3)",
                points_deducted=6,  # 6 branches - 3 threshold = 3 * 2 points
                line_number=1,
                function_name="test_func",
                is_red_flag=False
            )
        ]
        
        score = self.calculator.calculate_function_score("test_func", 1, violations)
        expected_final = 100 - 6  # 94
        assert score.final_score == expected_final
    
    def test_file_aggregation_worst_score(self):
        """Test that file aggregation uses worst score."""
        function_scores = [
            self.calculator.calculate_function_score("good_func", 1, []),  # 100
            self.calculator.calculate_function_score("bad_func", 10, [
                Violation("Constructor Side Effects", "Test", 15, 1, "bad_func", True)
            ]),  # 85
            self.calculator.calculate_function_score("worst_func", 20, [
                Violation("Non-Deterministic Time Usage", "Test", 10, 1, "worst_func", True),
                Violation("Randomness Usage", "Test", 10, 2, "worst_func", True),
                Violation("Global State Mutation", "Test", 10, 3, "worst_func", True)
            ])  # 70
        ]
        
        file_score = self.calculator.aggregate_file_score(function_scores, [])
        assert file_score == 70  # Should be worst score (70)
    
    def test_score_breakdown_accuracy(self):
        """Test score breakdown calculation accuracy."""
        violations = [
            Violation(
                rule_name="External Dependency Count",
                description="File System dependency",
                points_deducted=5,
                line_number=1,
                function_name="test_func",
                is_red_flag=False
            ),
            Violation(
                rule_name="Non-Deterministic Time Usage",
                description="Time dependency",
                points_deducted=10,
                line_number=2,
                function_name="test_func",
                is_red_flag=True
            ),
            Violation(
                rule_name="Constructor Side Effects",
                description="Constructor side effect",
                points_deducted=15,
                line_number=3,
                function_name="test_func",
                is_red_flag=True
            )
        ]
        
        breakdown = self.calculator.get_score_breakdown(violations)
        
        assert breakdown['baseline_score'] == 100
        assert breakdown['total_deductions'] == 30  # 5 + 10 + 15
        assert breakdown['final_score'] == 70  # 100 - 30
        assert breakdown['red_flag_count'] == 2
        
        # Check violations by rule
        assert 'External Dependency Count' in breakdown['violations_by_rule']
        assert 'Non-Deterministic Time Usage' in breakdown['violations_by_rule']
        assert 'Constructor Side Effects' in breakdown['violations_by_rule']
        
        assert breakdown['violations_by_rule']['External Dependency Count']['total_points'] == 5
        assert breakdown['violations_by_rule']['Non-Deterministic Time Usage']['total_points'] == 10
        assert breakdown['violations_by_rule']['Constructor Side Effects']['total_points'] == 15
    
    def test_empty_file_score(self):
        """Test that empty files get perfect score."""
        function_scores = []
        class_scores = []
        
        file_score = self.calculator.aggregate_file_score(function_scores, class_scores)
        assert file_score == 100
    
    def test_constructor_scoring(self):
        """Test constructor scoring in class aggregation."""
        constructor_violations = [
            Violation(
                rule_name="Constructor Side Effects",
                description="Constructor has side effects",
                points_deducted=15,
                line_number=1,
                function_name="TestClass.__init__",
                is_red_flag=True
            )
        ]
        
        class_score = self.calculator.calculate_class_score(
            "TestClass", 1, constructor_violations, []
        )
        
        # Class score should contain constructor violations
        assert len(class_score.constructor_violations) == 1
        assert class_score.constructor_violations[0].points_deducted == 15
    
    def test_project_description_scenarios(self):
        """Test scenarios based on project description examples."""
        
        # Scenario 1: Function with time dependency (-10 points)
        time_violations = [
            Violation(
                rule_name="Non-Deterministic Time Usage",
                description="Non-deterministic time usage",
                points_deducted=10,
                line_number=5,
                function_name="process_with_time",
                is_red_flag=True
            )
        ]
        
        score = self.calculator.calculate_function_score("process_with_time", 5, time_violations)
        assert score.final_score == 90  # 100 - 10
        
        # Scenario 2: Function with multiple dependencies
        multi_violations = [
            Violation("External Dependency Count", "File System", 5, 1, "func", False),
            Violation("Direct File I/O in Logic", "File operation", 10, 2, "func", False),
            Violation("Excessive Parameter Count", "Too many params", 5, 3, "func", False)
        ]
        
        score = self.calculator.calculate_function_score("func", 1, multi_violations)
        assert score.final_score == 80  # 100 - 5 - 10 - 5
        
        # Scenario 3: Function with red flags
        red_flag_violations = [
            Violation("Global State Mutation", "Global mutation", 10, 1, "func", True),
            Violation("Mixed I/O and Logic", "Mixed I/O", 8, 2, "func", True)
        ]
        
        score = self.calculator.calculate_function_score("func", 1, red_flag_violations)
        assert score.final_score == 82  # 100 - 10 - 8
        assert all(v.is_red_flag for v in red_flag_violations)
    
    def test_score_bands_validation(self):
        """Test that scores fall into correct bands."""
        from testability_analyzer.threshold_classifier import ThresholdClassifier
        
        classifier = ThresholdClassifier()
        
        # Test file-level bands
        assert classifier.classify_file_score(95) == "Healthy"
        assert classifier.classify_file_score(85) == "Healthy"
        assert classifier.classify_file_score(75) == "Caution"
        assert classifier.classify_file_score(65) == "Caution"
        assert classifier.classify_file_score(55) == "High Friction"
        assert classifier.classify_file_score(45) == "High Friction"
        assert classifier.classify_file_score(35) == "Refactor First"
        assert classifier.classify_file_score(25) == "Refactor First"
        
        # Test function-level bands
        assert classifier.classify_function_score(90) == "Easy"
        assert classifier.classify_function_score(80) == "Easy"
        assert classifier.classify_function_score(70) == "Testable"
        assert classifier.classify_function_score(60) == "Testable"
        assert classifier.classify_function_score(50) == "Hard"
        assert classifier.classify_function_score(40) == "Hard"
        assert classifier.classify_function_score(30) == "Painful"
        assert classifier.classify_function_score(20) == "Painful"
