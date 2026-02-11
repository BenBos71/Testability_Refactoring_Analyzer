## Context

The Testability Refactoring Analyzer is a new static analysis tool designed to help engineers understand and improve the testability of their Python code. Unlike existing tools that focus on bug detection or performance analysis, this tool specifically targets structural inhibitors that make unit testing difficult. The project requires building a complete Python package from scratch with a modular architecture that can handle AST parsing, rule evaluation, scoring, and reporting. The tool must be deterministic, conservative, and provide actionable guidance without relying on AI or runtime instrumentation.

## Goals / Non-Goals

**Goals:**
- Create a modular static analysis tool using Python AST for accurate code structure understanding
- Implement all 12 testability inhibitor rules with exact point deductions as specified
- Generate comprehensive reports with complete violation transparency (every violation listed with location and penalty)
- Provide both human-readable and machine-readable outputs for different use cases
- Establish clear, defensible thresholds that reflect the marginal cost of writing reliable unit tests
- Support CI/CD integration through structured JSON output

**Non-Goals:**
- Automatic test generation or runtime profiling
- AI-powered analysis or machine learning models
- Dynamic code execution or instrumentation
- Perfect accuracy (heuristics are expected and documented)
- Support for languages other than Python in v1

## Decisions

**Architecture: Modular Pipeline Design**
- **Decision**: Implement as a pipeline of independent components (parsing → rule evaluation → scoring → reporting)
- **Rationale**: Each component has clear responsibilities, making testing and maintenance easier. Allows for future extensibility (new rules, output formats).
- **Alternatives considered**: Monolithic analyzer class (rejected for complexity), plugin architecture (overkill for v1)

**AST Parsing Strategy**
- **Decision**: Use Python's built-in `ast` module with custom `ast.NodeVisitor` implementations
- **Rationale**: Most accurate and reliable way to understand Python code structure. No external dependencies needed.
- **Alternatives considered**: Regex-based parsing (inaccurate for complex syntax), third-party parsers (unnecessary dependency)

**Rule Evaluation Architecture**
- **Decision**: Create separate rule classes inheriting from a base `TestabilityRule` abstract class
- **Rationale**: Each rule can be developed, tested, and modified independently. Clear interface for adding new rules in future versions.
- **Alternatives considered**: Single large evaluation function (hard to maintain), configuration-driven rules (less flexible for complex patterns)

**Scoring System Design**
- **Decision**: Baseline 100 points with rule-specific deductions, tracked at function level with aggregation to class/file levels
- **Rationale**: Transparent and explainable scoring that matches the project description exactly. Easy to understand why code received its score.
- **Alternatives considered**: Complexity-based scoring (less transparent), weighted scoring system (more complex to explain)

**Report Generation Approach**
- **Decision**: Separate formatter classes for text and JSON outputs with shared data models
- **Rationale**: Clean separation of concerns. Same analysis data can be formatted differently without duplication.
- **Alternatives considered**: Template-based reports (less flexible), single formatter with conditionals (messy)

**CLI Interface**
- **Decision**: Use `argparse` for command-line interface with support for file/directory inputs and output format selection
- **Rationale**: Standard library solution, no external dependencies, familiar interface for developers.
- **Alternatives considered**: `click` library (additional dependency), custom argument parsing (reimplementing existing functionality)

## Risks / Trade-offs

**Performance Risk** → AST parsing can be slow for large codebases
- **Mitigation**: Implement incremental analysis, parallel file processing, and caching of parsed ASTs

**False Positives Risk** → Heuristic rules may flag acceptable patterns as violations
- **Mitigation**: Make rules conservative, provide clear documentation, allow configuration exceptions in future versions

**Maintenance Risk** → 12 separate rule classes require ongoing maintenance
- **Mitigation**: Comprehensive test suite, clear rule documentation, shared utility functions for common patterns

**Complexity Risk** → Modular architecture may have more overhead than simple implementation
- **Mitigation**: Focus on clean interfaces, document component interactions, use dependency injection for testability

**Accuracy Trade-off** → Conservative approach may miss some subtle testability issues
- **Acceptance**: Better to miss issues than to provide false guidance. Users can extend rules in future versions.

## Migration Plan

Since this is a new project, migration focuses on deployment and adoption:

1. **Development Phase**: Build core components with comprehensive unit tests
2. **Integration Testing**: Test with sample codebases representing different complexity levels
3. **CLI Testing**: Ensure command-line interface works for various input scenarios
4. **Documentation**: Complete user guide and rule documentation
5. **Release**: Package as installable Python tool via PyPI
6. **CI Integration**: Provide examples for GitHub Actions, GitLab CI integration

Rollback strategy: Version control allows reverting to previous releases if issues are discovered.

## Open Questions

- Should the tool support configuration files for customizing rule penalties or thresholds? (Deferred to v2)
- How should the tool handle Python files with syntax errors? (Skip with warning or fail fast?)
- Should there be an option to ignore specific rules or files? (Deferred to v2)
- What is the maximum reasonable file size the tool should attempt to parse?
