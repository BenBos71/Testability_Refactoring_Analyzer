## ADDED Requirements

### Requirement: Parse Python code structure
The system SHALL parse Python source files using AST to extract function and class definitions with their complete structure and relationships.

#### Scenario: Successful file parsing
- **WHEN** a valid Python file is provided
- **THEN** system extracts all function definitions with their bodies
- **AND** system extracts all class definitions with their methods
- **AND** system preserves the hierarchical structure of nested code elements

### Requirement: Detect code patterns and dependencies
The system SHALL analyze AST nodes to identify specific patterns related to testability inhibitors including function calls, imports, variable assignments, and control flow structures.

#### Scenario: Pattern detection in function
- **WHEN** analyzing a function body
- **THEN** system identifies all external function calls
- **AND** system identifies all import statements
- **AND** system identifies variable assignments and mutations
- **AND** system identifies control flow branches and loops

### Requirement: Handle Python syntax variations
The system SHALL handle various Python syntax constructs including decorators, comprehensions, async functions, and exception handling blocks.

#### Scenario: Complex syntax parsing
- **WHEN** encountering decorated functions or async functions
- **THEN** system correctly parses the underlying function structure
- **AND** system identifies patterns within exception handling blocks
- **AND** system processes list/dict/set comprehensions for embedded patterns
