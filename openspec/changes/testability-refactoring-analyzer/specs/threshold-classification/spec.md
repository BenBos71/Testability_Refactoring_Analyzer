## ADDED Requirements

### Requirement: Classify scores into testability bands
The system SHALL categorize testability scores into four bands: Healthy (80-100), Caution (60-79), High Friction (40-59), and Refactor First (below 40).

#### Scenario: Score classification
- **WHEN** classifying a testability score
- **THEN** system assigns Healthy band for scores 80-100
- **AND** system assigns Caution band for scores 60-79
- **AND** system assigns High Friction band for scores 40-59
- **AND** system assigns Refactor First band for scores below 40

### Requirement: Provide band-specific guidance
The system SHALL provide actionable recommendations tailored to each testability band classification.

#### Scenario: Band-specific recommendations
- **WHEN** providing guidance for Healthy scores
- **THEN** system indicates no action needed
- **WHEN** providing guidance for Caution scores
- **THEN** system recommends opportunistic refactoring
- **WHEN** providing guidance for High Friction scores
- **THEN** system recommends refactoring before feature work
- **WHEN** providing guidance for Refactor First scores
- **THEN** system recommends structural changes before any work

### Requirement: Flag structural red flags regardless of score
The system SHALL identify and prominently display structural testability smells that should trigger warnings even when overall scores are acceptable.

#### Scenario: Red flag identification
- **WHEN** analyzing code structure
- **THEN** system flags constructor I/O operations as red flags
- **AND** system flags global state mutations as red flags
- **AND** system flags non-determinism in core logic as red flags
- **AND** system flags networking combined with business logic as red flags
- **AND** system flags exception-driven control flow in hot paths as red flags

### Requirement: Apply function-level thresholds
The system SHALL apply function-specific score thresholds: Easy to test (75+), Testable with effort (55-74), Hard to test (35-54), Painful (below 35).

#### Scenario: Function-level classification
- **WHEN** classifying function scores
- **THEN** system applies Easy to test for scores 75+
- **AND** system applies Testable with effort for scores 55-74
- **AND** system applies Hard to test for scores 35-54
- **AND** system applies Painful for scores below 35
