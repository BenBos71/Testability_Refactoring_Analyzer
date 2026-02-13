## Context

The Testability Analyzer currently has basic testing with simple synthetic examples, but lacks comprehensive, professional-level code samples that demonstrate real-world scenarios across all score thresholds. The existing test_sample.py is minimal and doesn't showcase the tool's full capabilities or validate edge cases that users will encounter in production code.

## Goals / Non-Goals

**Goals:**
- Create professional Python examples covering all testability score bands (0-25, 26-50, 51-75, 76-100)
- Provide two healthy examples: one scoring 76-100 and one scoring perfect 100
- Demonstrate real-world code patterns (web APIs, data processing, OOP design)
- Validate analyzer accuracy and edge case handling
- Create reference examples for users learning testability principles
- Build benchmark suite for regression testing

**Non-Goals:**
- Modify existing analyzer functionality
- Create comprehensive test framework (unit tests already exist)
- Support Python versions outside 3.8+ scope
- Generate examples automatically (manual professional design required)

## Decisions

### File Organization
- **Decision**: Create `tests/examples/` subdirectory instead of `examples/` root
- **Rationale**: Keeps examples with test suite, follows Python project conventions, separates from production code

### Score Targeting Strategy
- **Decision**: Manual score targeting with validation rather than algorithmic generation
- **Rationale**: Ensures realistic examples, allows demonstration of specific anti-patterns, provides better learning value

### Example Categories
- **Decision**: Organize by score band and complexity level
- **Rationale**: Clear progression from simple to complex, helps users understand what makes code testable

### Perfect Score Validation
- **Decision**: Include explicit verification of 100-score analyzer output
- **Rationale**: Critical for validating analyzer correctness, provides regression baseline

## Risks / Trade-offs

### Risk: Subjective Example Quality
- **Mitigation**: Follow Python best practices, use real-world patterns, document design decisions

### Risk: Score Band Overlap
- **Mitigation**: Clear documentation of expected ranges, multiple examples per band, edge case coverage

### Trade-off: Manual vs Generated Examples
- **Chosen**: Manual professional design
- **Impact**: Higher quality but more time-intensive, better educational value
