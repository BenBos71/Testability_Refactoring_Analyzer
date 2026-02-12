"""
File system traversal utilities for analyzing multiple files and directories.

Provides utilities for finding Python files, handling different path types,
and managing batch analysis operations.
"""

import os
from pathlib import Path
from typing import List, Iterator, Generator


def find_python_files(paths: List[str]) -> List[Path]:
    """
    Find all Python files in the given paths.
    
    Args:
        paths: List of file or directory paths
        
    Returns:
        List of Path objects for Python files
    """
    python_files = []
    
    for path_str in paths:
        path = Path(path_str)
        
        if not path.exists():
            continue
        
        if path.is_file():
            if path.suffix == ".py":
                python_files.append(path)
        elif path.is_dir():
            # Recursively find all .py files
            python_files.extend(_find_python_files_recursive(path))
    
    return python_files


def _find_python_files_recursive(directory: Path) -> List[Path]:
    """
    Recursively find all Python files in a directory.
    
    Args:
        directory: Directory path to search
        
    Returns:
        List of Path objects for Python files
    """
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                python_files.append(file_path)
    
    return python_files


def is_python_file(file_path: Path) -> bool:
    """
    Check if a file is a Python file.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file is a Python file
    """
    return file_path.suffix == ".py"


def get_relative_path(file_path: Path, base_path: Path) -> str:
    """
    Get relative path from base path.
    
    Args:
        file_path: File path to make relative
        base_path: Base directory path
        
    Returns:
        Relative path as string
    """
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        # File is not relative to base path
        return str(file_path)


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists and is accessible.
    
    Args:
        directory_path: Directory path to check
        
    Returns:
        True if directory exists and is accessible
    """
    path = Path(directory_path)
    return path.exists() and path.is_dir()


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    try:
        return file_path.stat().st_size
    except OSError:
        return 0


def is_likely_test_file(file_path: Path) -> bool:
    """
    Check if a file is likely a test file.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file appears to be a test file
    """
    name = file_path.name.lower()
    test_indicators = [
        "test_", "_test.", "tests_", "_tests.",
        "conftest.py", "__init__.py"
    ]
    
    return any(indicator in name for indicator in test_indicators)


def filter_non_test_files(file_paths: List[Path]) -> List[Path]:
    """
    Filter out likely test files from a list of file paths.
    
    Args:
        file_paths: List of file paths to filter
        
    Returns:
        List of non-test file paths
    """
    return [path for path in file_paths if not is_likely_test_file(path)]
