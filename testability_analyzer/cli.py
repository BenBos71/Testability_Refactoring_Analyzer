"""
Command-line interface for the Testability Refactoring Analyzer.

Provides argparse-based CLI with support for file/directory inputs and output format selection.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

try:
    from .analyzer import TestabilityAnalyzer
    from .formatters.text_formatter import TextFormatter
    from .formatters.json_formatter import JSONFormatter
except ImportError:  # pragma: no cover
    from pathlib import Path as _Path

    sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    from testability_analyzer.analyzer import TestabilityAnalyzer
    from testability_analyzer.formatters.text_formatter import TextFormatter
    from testability_analyzer.formatters.json_formatter import JSONFormatter


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="testability-analyzer",
        description="Testability Analyzer - analyze Python code for testability issues and refactoring opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  testability-analyzer myfile.py
  testability-analyzer src/ --output json
  testability-analyzer . --output text --verbose
        """
    )
    
    parser.add_argument(
        "paths",
        nargs="+",
        help="Python files or directories to analyze"
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output with detailed explanations"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    return parser


def validate_paths(paths: List[str]) -> List[Path]:
    """Validate and convert input paths to Path objects."""
    valid_paths = []
    
    for path_str in paths:
        path = Path(path_str)
        
        if not path.exists():
            print(f"Error: Path '{path_str}' does not exist", file=sys.stderr)
            sys.exit(1)
        
        valid_paths.append(path)
    
    return valid_paths


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate input paths
    paths = validate_paths(args.paths)
    
    # Initialize analyzer
    analyzer = TestabilityAnalyzer()
    
    # Analyze all paths
    all_results = []
    had_analyzable_input = False
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            had_analyzable_input = True
            result = analyzer.analyze_file(str(path))
            all_results.append(result)
        elif path.is_dir():
            had_analyzable_input = True
            results = analyzer.analyze_directory(str(path))
            all_results.extend(results)
        else:
            print(f"Warning: Skipping non-Python file: {path}", file=sys.stderr)

    if not had_analyzable_input:
        print("Error: No Python files to analyze", file=sys.stderr)
        sys.exit(1)
    
    # Format and output results
    if args.output == "json":
        formatter = JSONFormatter(verbose=args.verbose)
    else:
        formatter = TextFormatter(verbose=args.verbose)
    
    output = formatter.format(all_results)
    print(output)


if __name__ == "__main__":
    main()
