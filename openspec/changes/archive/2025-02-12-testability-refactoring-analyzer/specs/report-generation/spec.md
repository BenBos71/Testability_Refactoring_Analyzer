## ADDED Requirements

### Requirement: Generate human-readable text reports
The system SHALL generate formatted text reports that display testability scores, findings, and refactoring suggestions in a clear, readable format for engineers.

#### Scenario: Text report generation
- **WHEN** generating a text report
- **THEN** system displays overall testability score with classification
- **AND** system lists per-function and per-class findings with exact locations
- **AND** system provides ranked list of testability inhibitors with point deductions
- **AND** system includes concrete refactoring suggestions for each issue
- **AND** system displays red flag violations prominently
- **AND** system shows optional refactoring suggestions separately from critical issues

### Requirement: Generate machine-readable JSON reports
The system SHALL generate structured JSON reports containing all analysis data suitable for CI/CD integration and programmatic processing.

#### Scenario: JSON report generation
- **WHEN** generating a JSON report
- **THEN** system includes overall score and classification
- **AND** system includes detailed function-level analysis with exact violations
- **AND** system includes rule violation details with locations and point deductions
- **AND** system includes refactoring suggestions in structured format
- **AND** system distinguishes between red flag violations and optional suggestions
- **AND** system includes complete score breakdown calculations

### Requirement: Format scores with classifications
The system SHALL format testability scores with appropriate classifications (Healthy, Caution, High Friction, Refactor First) and color coding for text reports.

#### Scenario: Score formatting
- **WHEN** displaying scores in reports
- **THEN** system applies correct classification bands
- **AND** system provides actionable guidance for each classification
- **AND** system highlights files requiring immediate attention

### Requirement: Map refactoring suggestions to detected issues
The system SHALL provide specific, actionable refactoring suggestions directly linked to each detected testability inhibitor.

#### Scenario: Suggestion mapping
- **WHEN** generating refactoring suggestions
- **THEN** system provides specific guidance for external dependencies
- **AND** system provides specific guidance for file I/O issues
- **AND** system provides specific guidance for non-determinism (time and randomness)
- **AND** system provides specific guidance for global state mutations
- **AND** system provides specific guidance for structural issues (branching, parameters, observability)
- **AND** system provides specific guidance for constructor side effects
- **AND** system provides specific guidance for mixed I/O and logic
- **AND** system provides specific guidance for exception-driven control flow
- **AND** system provides specific guidance for hidden dependencies
- **AND** system clearly distinguishes between critical suggestions and optional improvements
