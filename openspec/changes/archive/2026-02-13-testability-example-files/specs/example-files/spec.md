## ADDED Requirements

### Requirement: Example Files Creation
The system SHALL provide professional Python example files demonstrating all testability score bands and real-world code patterns.

#### Scenario: Perfect Score Example (100)
- **WHEN** user runs analyzer on perfect code example
- **THEN** system shall report score of 100 with no violations

#### Scenario: Healthy Score Example (76-100)
- **WHEN** user runs analyzer on healthy code example
- **THEN** system shall report score between 76-100 with minor violations

#### Scenario: Caution Score Example (51-75)
- **WHEN** user runs analyzer on caution code example
- **THEN** system shall report score between 51-75 with moderate violations

#### Scenario: High Friction Score Example (26-50)
- **WHEN** user runs analyzer on high friction code example
- **THEN** system shall report score between 26-50 with significant violations

#### Scenario: Refactor First Score Example (0-25)
- **WHEN** user runs analyzer on refactor first code example
- **THEN** system shall report score between 0-25 with critical violations

#### Scenario: Professional Code Quality
- **WHEN** user examines example files
- **THEN** code shall follow Python best practices and real-world patterns

#### Scenario: Documentation Standards
- **WHEN** user reads example files
- **THEN** each file shall include clear documentation explaining purpose and expected score range
