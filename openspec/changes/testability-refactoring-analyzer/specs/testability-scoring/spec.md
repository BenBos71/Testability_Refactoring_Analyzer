## ADDED Requirements

### Requirement: Calculate baseline testability score
The system SHALL start each function with a baseline score of 100 points and subtract points for detected testability inhibitors according to the defined rule penalties.

#### Scenario: Initial score calculation
- **WHEN** analyzing a new function
- **THEN** system sets initial score to 100
- **AND** system applies penalty deductions for each detected inhibitor
- **AND** system ensures final score never goes below 0

### Requirement: Aggregate scores at multiple levels
The system SHALL calculate testability scores at function, class, and file levels by appropriately aggregating individual component scores using weighted averages.

#### Scenario: File-level score aggregation
- **WHEN** calculating file-level score
- **THEN** system aggregates all function scores within the file
- **AND** system incorporates class constructor penalties
- **AND** system applies appropriate weighting for file-level assessment

### Requirement: Provide score breakdown explanations
The system SHALL provide detailed breakdowns showing exactly which rules contributed to score deductions and the point values subtracted for each violation.

#### Scenario: Score explanation generation
- **WHEN** generating score breakdown
- **THEN** system lists each detected inhibitor with its penalty
- **AND** system shows the calculation from baseline to final score
- **AND** system prioritizes higher-impact inhibitors in the explanation
