## Why

Engineers working on legacy, safety-critical, and systems-oriented software struggle to write reliable unit tests due to structural testability inhibitors in their code. Current static analysis tools focus on bugs and performance, but don't explain WHY code is difficult to test or provide actionable refactoring guidance. This creates a cycle of brittle tests, avoided testing, and technical debt that accumulates over time.

## What Changes

- Create a static analysis tool that evaluates Python code testability using deterministic, heuristic-based rules
- Implement 12 specific testability inhibitor detection rules covering dependencies, I/O, non-determinism, global state, and structural issues
- Generate explainable testability scores (0-100) with per-function and per-class breakdowns
- Provide concrete, rules-based refactoring suggestions mapped to detected issues
- Output both human-readable reports and machine-readable JSON for CI integration
- Establish defensible thresholds that reflect the marginal cost of writing reliable unit tests

## Capabilities

### New Capabilities
- `static-analysis-engine`: Core Python AST parsing and analysis framework for traversing code structure and detecting patterns
- `testability-scoring`: Algorithm that calculates testability scores starting from 100 and subtracting points based on detected inhibitors
- `rule-evaluation`: Implementation of 12 specific testability rules including external dependency counting, file I/O detection, time usage, randomness, global state mutation, and structural complexity analysis
- `report-generation`: Formatters for creating human-readable text reports and machine-readable JSON outputs with scores, findings, and refactoring suggestions
- `threshold-classification`: System for categorizing scores into bands (Healthy, Caution, High Friction, Refactor First) with actionable guidance

### Modified Capabilities
- None - this is a new project with no existing capabilities

## Impact

- **Code**: New Python package implementing the analyzer with modular architecture
- **Dependencies**: Python AST library, standard file system access, no external AI or runtime dependencies
- **CLI**: Command-line interface for analyzing Python files and directories
- **Integration**: JSON output enables CI/CD pipeline integration for testability gating
- **Documentation**: Comprehensive rule documentation and refactoring guidance
