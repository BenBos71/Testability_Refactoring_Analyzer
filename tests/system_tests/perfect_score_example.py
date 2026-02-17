"""Perfect Score Example - Testability Score: 100

This file demonstrates ideal testability with zero violations.
It should score exactly 100 points when analyzed by the Testability Analyzer.

Expected Score: 100
Expected Classification: Healthy
Expected Violations: None
"""

def add(a: int, b: int) -> int:
    """Add two integers with proper validation."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    return a + b

def multiply(x: int, y: int) -> int:
    """Multiply two integers with proper validation."""
    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError("Both arguments must be integers")
    return x * y

def calculate_sum(numbers: list) -> int:
    """Calculate sum of numbers with proper validation."""
    if not numbers:
        raise ValueError("Cannot calculate sum of empty list")
    total = sum(numbers)
    return total

def calculate_product(numbers: list) -> int:
    """Calculate product of numbers with proper validation."""
    if not numbers:
        raise ValueError("Cannot calculate product of empty list")
    result = 1
    for num in numbers:
        result *= num
    return result

def get_result_summary(results: list) -> str:
    """Get summary of calculation results."""
    return f"Processed {len(results)} operations successfully"
