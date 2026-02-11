## ADDED Requirements

### Requirement: Detect external dependency types
The system SHALL identify distinct external dependency types including file system access, environment variables, network calls, OS-level calls, and module-level singletons.

#### Scenario: External dependency detection
- **WHEN** analyzing function calls
- **THEN** system identifies file system operations (open, read, write, remove)
- **AND** system identifies environment variable access (os.environ, getenv)
- **AND** system identifies network calls (requests, socket, urllib)
- **AND** system identifies OS-level calls (subprocess, sys, platform)
- **AND** system identifies module-level singleton usage

### Requirement: Detect file I/O in business logic
The system SHALL identify direct file I/O operations within non-I/O-specific functions including file reads, writes, and filesystem API calls.

#### Scenario: File I/O detection
- **WHEN** analyzing a function body
- **THEN** system detects calls to open() and file operations
- **AND** system detects pathlib operations
- **AND** system detects os.path and os filesystem calls
- **AND** system excludes functions whose primary purpose is I/O

### Requirement: Detect non-deterministic time usage
The system SHALL identify calls to time-dependent functions including time.time, datetime.now, datetime.utcnow that introduce non-determinism.

#### Scenario: Time dependency detection
- **WHEN** analyzing function calls
- **THEN** system detects time.time() calls
- **AND** system detects datetime.now() calls
- **AND** system detects datetime.utcnow() calls
- **AND** system flags these as non-deterministic inhibitors

### Requirement: Detect randomness usage
The system SHALL identify calls to random number generators and UUID generators that prevent deterministic test execution.

#### Scenario: Randomness detection
- **WHEN** analyzing function calls
- **THEN** system detects random module usage (random.random, random.choice)
- **AND** system detects uuid.uuid4() and uuid.uuid1() calls
- **AND** system flags these as randomness inhibitors

### Requirement: Detect global state mutation
The system SHALL identify assignments to module-level variables, global objects, and singletons that create test order dependencies.

#### Scenario: Global state detection
- **WHEN** analyzing variable assignments
- **THEN** system detects module-level variable mutations
- **AND** system detects global keyword usage
- **AND** system detects singleton object modifications
- **AND** system flags these as global state inhibitors

### Requirement: Detect mixed I/O and logic
The system SHALL identify functions that perform both I/O operations and return computed values, preventing isolated testing.

#### Scenario: Mixed I/O and logic detection
- **WHEN** analyzing function structure
- **THEN** system identifies functions with both I/O calls
- **AND** system identifies functions that return computed values
- **AND** system flags functions combining both behaviors

### Requirement: Detect excessive branching complexity
The system SHALL count conditional branches including if/elif statements, match statements, and ternary expressions to identify functions with high cyclomatic complexity.

#### Scenario: Branch complexity detection
- **WHEN** analyzing control flow
- **THEN** system counts if/elif/else branches
- **AND** system counts match/case branches
- **AND** system counts ternary expressions
- **AND** system applies penalties after 3 branches

### Requirement: Detect exception-driven control flow
The system SHALL identify exceptions raised as part of normal logic paths rather than exceptional circumstances.

#### Scenario: Exception control flow detection
- **WHEN** analyzing exception handling
- **THEN** system identifies custom exception raises in main logic paths
- **AND** system distinguishes between error handling and control flow
- **AND** system flags inappropriate exception usage

### Requirement: Detect constructor side effects
The system SHALL identify __init__ methods that perform I/O, time access, global mutations, or network calls.

#### Scenario: Constructor side effects detection
- **WHEN** analyzing class constructors
- **THEN** system detects I/O operations in __init__
- **AND** system detects time access in __init__
- **AND** system detects global mutations in __init__
- **AND** system detects network calls in __init__

### Requirement: Detect hidden dependencies via imports-in-function
The system SHALL identify import statements used inside functions instead of at module scope.

#### Scenario: Hidden import detection
- **WHEN** analyzing function bodies
- **THEN** system detects import statements within functions
- **AND** system detects from...import statements within functions
- **AND** system flags these as hidden dependencies

### Requirement: Detect excessive parameter count
The system SHALL identify functions with more than 5 parameters which may indicate missing abstractions.

#### Scenario: Parameter count detection
- **WHEN** analyzing function signatures
- **THEN** system counts function parameters
- **AND** system flags functions with >5 parameters
- **AND** system excludes *args and **kwargs from base count

### Requirement: Detect low observability
The system SHALL identify functions that perform work but have no return value and do not emit structured outputs.

#### Scenario: Observability detection
- **WHEN** analyzing function behavior
- **THEN** system identifies functions with no return value
- **AND** system identifies functions without structured output emission
- **AND** system flags functions with unobservable outcomes
