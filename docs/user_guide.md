# Testability Analyzer User Guide

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Line Usage](#command-line-usage)
- [Understanding the Output](#understanding-the-output)
- [Testability Rules](#testability-rules)
- [Scoring System](#scoring-system)
- [Integration with CI/CD](#integration-with-cicd)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install from PyPI

```bash
pip install testability-analyzer
```

### Install from Source

```bash
git clone https://github.com/BenBos71/Testability_Refactoring_Analyzer.git
cd Testability_Refactoring_Analyzer
pip install -e .
```

### Verify Installation

```bash
testability-analyzer --version
# Should output: testability-analyzer 0.1.0
```

## Quick Start

### Analyze a Single File

```bash
testability-analyzer myfile.py
```

### Analyze a Directory

```bash
testability-analyzer src/
```

### Get JSON Output for CI/CD

```bash
testability-analyzer src/ --output json
```

### Get Detailed Verbose Output

```bash
testability-analyzer src/ --verbose
```

## Command Line Usage

### Basic Syntax

```bash
testability-analyzer [OPTIONS] PATHS...
```

### Arguments

- `PATHS`: One or more Python files or directories to analyze

### Options

- `--output, -o`: Output format (`text` or `json`, default: `text`)
- `--verbose, -v`: Enable verbose output with detailed explanations
- `--version`: Show version information
- `--help`: Show help message

### Examples

```bash
# Analyze multiple files
testability-analyzer file1.py file2.py file3.py

# Analyze multiple directories
testability-analyzer src/ tests/

# Mixed files and directories
testability-analyzer main.py src/ tests/

# JSON output for automation
testability-analyzer src/ --output json > results.json

# Verbose text output
testability-analyzer src/ --verbose

# Combine options
testability-analyzer src/ --output json --verbose > detailed_results.json
```

## Understanding the Output

### Text Output Format

The text output provides a human-readable report with the following sections:

#### Header
```
Testability Analysis Report
==================================================
```

#### Summary
```
Summary:
Files analyzed: 5
Functions analyzed: 23
Classes analyzed: 8
Average score: 72.3
```

#### File Details
For each file, you'll see:
- File path and overall score
- Classification (Healthy, Caution, High Friction, Refactor First)
- Red flags (if any)
- Function scores
- Class scores

#### Red Flags Section
```
🚨 RED FLAGS:
  • Non-Deterministic Time Usage (line 15) - Non-deterministic time usage makes testing difficult [-10 points]
  • Constructor Side Effects (line 21) - Constructor has side effects [-15 points]
```

### JSON Output Format

The JSON output provides structured data suitable for programmatic processing:

```json
{
  "metadata": {
    "tool": "Testability Analyzer",
    "version": "0.1.0",
    "timestamp": "2025-02-12T14:30:00.000000",
    "format_version": "1.0"
  },
  "summary": {
    "total_files": 5,
    "total_functions": 23,
    "total_classes": 8,
    "total_violations": 45,
    "total_red_flags": 8,
    "score_statistics": {
      "average": 72.3,
      "minimum": 35.0,
      "maximum": 95.0
    },
    "classifications": {
      "Healthy": 2,
      "Caution": 2,
      "High Friction": 1,
      "Refactor First": 0
    }
  },
  "files": [...]
}
```

## Testability Rules

The analyzer evaluates your code against 12 testability rules:

### Red Flag Rules (Always Critical)

1. **Constructor Side Effects** (-15 points)
   - Constructors that perform I/O, network calls, or other side effects
   - Makes object instantiation difficult to test

2. **Global State Mutation** (-10 points)
   - Functions that modify global variables
   - Creates hidden dependencies between tests

3. **Non-Deterministic Time Usage** (-10 points)
   - Using `time.time()`, `datetime.now()`, etc.
   - Makes tests non-reproducible

4. **Mixed I/O and Logic** (-8 points)
   - Functions that mix business logic with I/O operations
   - Violates separation of concerns

5. **Exception-Driven Control Flow** (-5 points)
   - Using exceptions for normal program flow
   - Obscures the actual logic path

### Standard Rules

6. **Direct File I/O in Logic** (-10 points)
   - File operations embedded in business logic
   - Makes testing require file system setup

7. **Randomness Usage** (-10 points)
   - Using random number generators
   - Makes test results unpredictable

8. **External Dependency Count** (-5 points per distinct type)
   - Dependencies on external systems (files, network, databases, etc.)
   - Increases test setup complexity

9. **Hidden Dependencies via Imports-in-Function** (-5 points)
   - Import statements inside functions
   - Hides dependencies from the module interface

10. **Excessive Parameter Count** (-5 points)
    - Functions with more than 5 parameters
    - Indicates high complexity and coupling

11. **Low Observability** (-5 points)
    - Functions without return values, logging, or assertions
    - Difficult to verify behavior in tests

12. **Branch Explosion Risk** (-2 points per branch after 3)
    - Excessive conditional branching
    - Increases test case complexity

## Scoring System

### Baseline Score
- All functions start with a baseline score of 100 points
- Points are deducted for each rule violation

### Score Bands

#### File-Level Classification
- **Healthy (80-100)**: Well-structured, easily testable code
- **Caution (60-79)**: Some testability issues, moderate effort to improve
- **High Friction (40-59)**: Significant testability problems, major refactoring needed
- **Refactor First (<40)**: Critical testability issues, refactor before adding features

#### Function-Level Classification
- **Easy (75+)**: Straightforward to test with minimal setup
- **Testable (55-74)**: Testable with some setup or mocking
- **Hard (35-54)**: Difficult to test, requires significant setup
- **Painful (<35)**: Very difficult to test, consider redesign

### Score Calculation Example

```python
def process_data(data):
    import requests  # Hidden import: -5 points
    start_time = time.time()  # Time usage: -10 points
    
    with open('output.txt', 'w') as f:  # File I/O: -10 points
        f.write(str(data))
    
    return data.upper()
```

Final score: 100 - 5 - 10 - 10 = **65 points** (Caution band)

## Integration with CI/CD

### GitHub Actions

```yaml
name: Testability Analysis
on: [push, pull_request]

jobs:
  testability:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install testability-analyzer
    - name: Run testability analysis
      run: |
        testability-analyzer src/ --output json > testability_results.json
    - name: Upload results
      uses: actions/upload-artifact@v2
      with:
        name: testability-results
        path: testability_results.json
```

### GitLab CI

```yaml
testability:
  stage: test
  image: python:3.8
  script:
    - pip install testability-analyzer
    - testability-analyzer src/ --output json > testability_results.json
  artifacts:
    reports:
      junit: testability_results.json
  only:
    - merge_requests
    - main
```

### Quality Gates

You can use the JSON output to enforce quality gates:

```bash
#!/bin/bash
# Extract average score from JSON output
avg_score=$(testability-analyzer src/ --output json | jq -r '.summary.score_statistics.average')

# Fail if average score is below threshold
if (( $(echo "$avg_score < 70" | bc -l) )); then
  echo "Average testability score ($avg_score) is below threshold (70)"
  exit 1
fi
```

## Advanced Usage

### Analyzing Specific Patterns

```bash
# Analyze only test files (excluded by default)
testability-analyzer tests/ --verbose

# Analyze configuration files separately
testability-analyzer config/ setup.py
```

### Combining with Other Tools

```bash
# Run testability analysis alongside other quality checks
testability-analyzer src/ --output json > testability.json
black --check src/
flake8 src/
mypy src/
```

### Custom Scripts

```python
#!/usr/bin/env python3
import json
import sys
from testability_analyzer.analyzer import TestabilityAnalyzer

def analyze_and_filter(directory, min_score=70):
    analyzer = TestabilityAnalyzer()
    results = analyzer.analyze_directory(directory)
    
    low_score_files = [f for f in results if f.overall_score < min_score]
    
    if low_score_files:
        print(f"Files with score < {min_score}:")
        for file_result in low_score_files:
            print(f"  {file_result.file_path}: {file_result.overall_score}")
        return 1
    else:
        print(f"All files have score >= {min_score}")
        return 0

if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else "src/"
    min_score = int(sys.argv[2]) if len(sys.argv) > 2 else 70
    sys.exit(analyze_and_filter(directory, min_score))
```

## Troubleshooting

### Common Issues

#### "File does not exist" Error
```bash
# Check file exists and is accessible
ls -la myfile.py

# Use absolute path if needed
testability-analyzer /full/path/to/myfile.py
```

#### "Could not parse file" Warning
- Check for syntax errors in the Python file
- Ensure file encoding is UTF-8
- Verify file is not corrupted

#### Low Scores on Well-Structured Code
- Check for hidden imports inside functions
- Verify constructors don't have side effects
- Look for time or randomness dependencies

#### Performance Issues
- Exclude large test directories: `testability-analyzer src/ --exclude tests/`
- Use JSON output for faster processing: `--output json`
- Analyze specific files instead of entire codebase

### Getting Help

```bash
# Show all options
testability-analyzer --help

# Get verbose output for debugging
testability-analyzer problematic_file.py --verbose

# Check version
testability-analyzer --version
```

### Reporting Issues

If you encounter issues or unexpected behavior:

1. Run with verbose mode: `--verbose`
2. Check the JSON output for structured data
3. Verify your code follows Python syntax
4. Report issues on the GitHub repository with:
   - Sample code that reproduces the issue
   - Expected vs actual behavior
   - Version information

### Tips for Better Results

1. **Run on Source Code Only**: Exclude test files, build artifacts, and generated code
2. **Use Verbose Mode**: Get detailed explanations for violations
3. **Focus on Red Flags**: Prioritize fixing red flag violations first
4. **Iterative Improvement**: Fix issues incrementally and re-analyze
5. **Team Guidelines**: Establish team-wide testability standards

## Best Practices

### Before Analysis
- Ensure code compiles without syntax errors
- Remove or exclude test files from analysis
- Check for proper module structure

### During Analysis
- Use verbose mode for detailed feedback
- Focus on red flags and high-impact violations
- Consider the context of your codebase

### After Analysis
- Prioritize red flag violations
- Address issues in order of impact
- Re-run analysis to verify improvements
- Establish quality gates for CI/CD

### Integration Tips
- Set minimum score thresholds for CI/CD
- Use JSON output for automated processing
- Track score trends over time
- Combine with other quality metrics
