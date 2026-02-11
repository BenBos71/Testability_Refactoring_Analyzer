## ADDED Requirements

### Requirement: Generate human-readable text reports
The system SHALL generate formatted text reports that display testability scores, findings, and refactoring suggestions in a clear, readable format for engineers.

#### Scenario: Text report generation
- **WHEN** generating a text report
- **THEN** system displays overall testability score with classification
- **AND** system lists per-function and per-class findings
- **AND** system provides ranked list of testability inhibitors
- **AND** system includes concrete refactoring suggestions for each issue

### Requirement: Generate machine-readable JSON reports
The system SHALL generate structured JSON reports containing all analysis data suitable for CI/CD integration and programmatic processing.

#### Scenario: JSON report generation
- **WHEN** generating a JSON report
- **THEN** system includes overall score and classification
- **AND** system includes detailed function-level analysis
- **AND** system includes rule violation details with locations
- **AND** system includes refactoring suggestions in structured format

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
- **AND** system provides specific guidance for non-determinism
- **AND** system provides specific guidance for global state mutations
- **AND** system provides specific guidance for structural issues
