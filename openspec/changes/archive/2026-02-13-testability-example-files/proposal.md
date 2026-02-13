## Why

The Testability Analyzer needs comprehensive, professional-level example files to validate that each scoring threshold (Healthy, Caution, High Friction, Refactor First) works correctly across different complexity levels and code patterns. Currently, testing relies on simple synthetic examples that may not reflect real-world code patterns and edge cases that users will encounter.

## What Changes

- Create `tests/examples/` subfolder with professional Python files
- Build examples covering all testability score bands (0-25, 26-50, 51-75, 76-100)
- Include **two healthy examples**: one scoring 76-100 (within healthy range) and one scoring perfect 100
- Ensure examples demonstrate real-world patterns and anti-patterns
- Add documentation explaining each example's purpose and expected score range
- Verify analyzer output for perfect 100 score case

## Capabilities

### New Capabilities
- `example-files`: Professional testability examples covering all score thresholds and real-world code patterns

### Modified Capabilities
- None (existing analyzer functionality unchanged)

## Impact

- Validates analyzer accuracy across all score bands
- Provides reference examples for users learning testability principles
- Enhances test coverage with realistic scenarios
- Demonstrates tool capabilities with practical, production-level code
- Creates benchmark suite for regression testing
