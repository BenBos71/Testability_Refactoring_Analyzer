from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from testability_analyzer.analyzer import TestabilityAnalyzer


@dataclass(frozen=True)
class Expectation:
    min_score: int
    max_score: int


EXPECTATIONS: dict[str, Expectation] = {
    "perfect_score_example.py": Expectation(min_score=100, max_score=100),
    "upper_healthy_example.py": Expectation(min_score=90, max_score=100),
    "healthy_range_example.py": Expectation(min_score=76, max_score=100),
    "caution_low_example.py": Expectation(min_score=51, max_score=65),
    "caution_high_example.py": Expectation(min_score=66, max_score=75),
    "friction_low_example.py": Expectation(min_score=26, max_score=40),
    "friction_high_example.py": Expectation(min_score=41, max_score=50),
    "refactor_low_example.py": Expectation(min_score=0, max_score=15),
    "refactor_high_example.py": Expectation(min_score=16, max_score=25),
}


def main() -> int:
    analyzer = TestabilityAnalyzer()

    base_dir = Path(__file__).resolve().parent
    example_files = sorted(
        [p for p in base_dir.glob("*.py") if p.name not in {"__init__.py", "validate_examples.py"}]
    )

    failures: list[str] = []
    results: list[tuple[str, int, str]] = []

    for file_path in example_files:
        file_score = analyzer.analyze_file(str(file_path))
        results.append((file_path.name, file_score.overall_score, file_score.classification))

        expectation = EXPECTATIONS.get(file_path.name)
        if expectation is None:
            continue

        if not (expectation.min_score <= file_score.overall_score <= expectation.max_score):
            failures.append(
                f"{file_path.name}: expected {expectation.min_score}-{expectation.max_score}, got {file_score.overall_score} ({file_score.classification})"
            )

    print("Example Validation Results")
    print("=" * 60)
    for name, score, classification in results:
        suffix = ""
        expectation = EXPECTATIONS.get(name)
        if expectation is not None:
            suffix = f" (expected {expectation.min_score}-{expectation.max_score})"
        print(f"{name}: {score} [{classification}]{suffix}")

    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nAll expected score ranges validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
