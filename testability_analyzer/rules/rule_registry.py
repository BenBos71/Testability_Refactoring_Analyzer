"""
Registry for managing all testability rules.

Provides centralized access to all rules and enables easy rule discovery
and evaluation coordination.
"""

from typing import List, Dict, Any
from ..base import TestabilityRule

from .external_dependency_rule import ExternalDependencyRule
from .file_io_rule import FileIORule
from .time_usage_rule import TimeUsageRule
from .randomness_rule import RandomnessRule
from .global_state_rule import GlobalStateRule
from .mixed_io_logic_rule import MixedIOLogicRule
from .branch_explosion_rule import BranchExplosionRule
from .exception_control_flow_rule import ExceptionControlFlowRule
from .constructor_side_effects_rule import ConstructorSideEffectsRule
from .hidden_imports_rule import HiddenImportsRule
from .parameter_count_rule import ParameterCountRule
from .observability_rule import ObservabilityRule


class RuleRegistry:
    """Registry for all testability rules."""
    
    def __init__(self):
        self._rules = [
            FileIORule(),
            TimeUsageRule(),
            RandomnessRule(),
            GlobalStateRule(),
            MixedIOLogicRule(),
            BranchExplosionRule(),
            ExceptionControlFlowRule(),
            ConstructorSideEffectsRule(),
            HiddenImportsRule(),
            ParameterCountRule(),
            ObservabilityRule(),
        ]
    
    def get_all_rules(self) -> List[TestabilityRule]:
        """
        Get all registered rules.
        
        Returns:
            List of all TestabilityRule instances
        """
        return self._rules
    
    def get_rule_by_name(self, name: str) -> TestabilityRule:
        """
        Get a specific rule by name.
        
        Args:
            name: Name of the rule to retrieve
            
        Returns:
            TestabilityRule instance or None if not found
        """
        for rule in self._rules:
            if rule.rule_name == name:
                return rule
        return None
    
    def get_red_flag_rules(self) -> List[TestabilityRule]:
        """
        Get all rules that generate red flags.
        
        Returns:
            List of rules that should always be flagged
        """
        red_flag_rules = []
        for rule in self._rules:
            if rule.rule_name in [
                "Constructor Side Effects",
                "Global State Mutation", 
                "Non-Deterministic Time Usage",
                "Mixed I/O and Logic",
                "Exception-Driven Control Flow"
            ]:
                red_flag_rules.append(rule)
        
        return red_flag_rules
