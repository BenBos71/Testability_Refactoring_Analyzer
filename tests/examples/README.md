# Testability Analyzer Examples

This directory contains professional Python example files designed to validate the Testability Analyzer across all score thresholds and real-world code patterns.

## 📊 Score Bands Covered

| Score Range | Classification | Examples |
|-------------|-------------|---------|
| 76-100 | Healthy | `upper_healthy_example.py`, `healthy_range_example.py` |
| 51-75 | Caution | `caution_high_example.py`, `caution_low_example.py` |
| 26-50 | High Friction | `friction_high_example.py`, `friction_low_example.py` |
| 0-25 | Refactor First | `refactor_high_example.py`, `refactor_low_example.py` |

## 🎯 Special Examples

### Perfect Score (100)
- `perfect_score_example.py` - Demonstrates ideal testability with zero violations

### Healthy Score Examples (76-100)
- `healthy_range_example.py` - Realistic invoice-style logic with small, non-red-flag complexity to land in the **Healthy** band (target: **76-100**)
- `upper_healthy_example.py` - Simple formatting/normalization logic designed to stay in the **upper Healthy** range (target: **90-100**), with a small intentional deduction (parameter count)

### Caution Score Examples (51-75)
- `caution_low_example.py` - Manual-review style scoring with heavier branching to land in the **lower Caution** range (target: **51-65**)
- `caution_high_example.py` - Similar scoring logic with fewer decision points to land in the **upper Caution** range (target: **66-75**)

### High Friction Examples (26-50)
- `friction_low_example.py` - Heavy mix of non-determinism, I/O, and branching intended to land in the **lower High Friction** range (target: **26-40**)
- `friction_high_example.py` - Still high friction, but slightly less extreme (target: **41-50**)

### Refactor First Examples (0-25)
- `refactor_low_example.py` - Multiple red-flag patterns and heavy complexity intended to land in the **lowest Refactor First** range (target: **0-15**)
- `refactor_high_example.py` - Still "Refactor First" but slightly less extreme (target: **16-25**)

### Real-World Patterns
- `web_api_example.py` - Common API patterns and async handling
- `data_processing_example.py` - Data pipelines and transformation logic
- `oop_design_example.py` - Complex object-oriented design patterns

## 🚀 Usage

```bash
# Test individual examples
testability-analyzer tests/examples/perfect_score_example.py

# If the console entrypoint isn't available in your environment:
python3 -m testability_analyzer.cli tests/examples/perfect_score_example.py

# Test all examples
testability-analyzer tests/examples/ --verbose

# If the console entrypoint isn't available in your environment:
python3 -m testability_analyzer.cli tests/examples/ --verbose

# Generate validation report
python3 tests/examples/validate_examples.py
```

## 📋 Expected Scores

Each example includes documentation explaining its expected score range and the specific testability issues it demonstrates.

## ✅ Expected vs Actual (Current)

| File | Expected | Actual |
|------|----------|--------|
| `perfect_score_example.py` | 100 | 100 |
| `upper_healthy_example.py` | 90-100 | 95 |
| `healthy_range_example.py` | 76-100 | 83 |
| `caution_low_example.py` | 51-65 | 63 |
| `caution_high_example.py` | 66-75 | 71 |
| `friction_low_example.py` | 26-40 | 40 |
| `friction_high_example.py` | 41-50 | 46 |
| `refactor_low_example.py` | 0-15 | 3 |
| `refactor_high_example.py` | 16-25 | 19 |

## 🔍 Validation

Run the validation script to verify all examples produce expected scores:
```bash
python3 tests/examples/validate_examples.py
```

This helps ensure the Testability Analyzer works correctly across all score thresholds!
