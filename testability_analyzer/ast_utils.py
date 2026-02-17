"""
AST parsing utilities for traversing Python code structure.

Provides utilities for parsing Python files, extracting functions and classes,
and building analysis context for rule evaluation.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field


@dataclass
class AnalysisContext:
    """Context information gathered during AST traversal."""
    imports: set = field(default_factory=set)
    global_variables: set = field(default_factory=set)
    functions: list = field(default_factory=list)
    classes: list = field(default_factory=list)
    current_function: Optional[str] = None
    current_class: Optional[str] = None


class ASTVisitor(ast.NodeVisitor):
    """Enhanced AST visitor that builds analysis context."""
    
    def __init__(self):
        self.context = AnalysisContext()
    
    def visit_Import(self, node: ast.Import) -> None:
        """Track import statements."""
        for alias in node.names:
            self.context.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from-import statements."""
        if node.module:
            self.context.imports.add(node.module)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function definitions."""
        self.context.functions.append(node.name)
        old_function = self.context.current_function
        self.context.current_function = node.name
        
        self.generic_visit(node)
        
        self.context.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function definitions."""
        self.context.functions.append(node.name)
        old_function = self.context.current_function
        self.context.current_function = node.name
        
        self.generic_visit(node)
        
        self.context.current_function = old_function
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class definitions."""
        self.context.classes.append(node.name)
        old_class = self.context.current_class
        self.context.current_class = node.name
        
        # Handle decorators
        for decorator in node.decorator_list:
            self._visit_decorator(decorator)
        
        self.generic_visit(node)
        
        self.context.current_class = old_class
    
    def _visit_decorator(self, decorator: ast.AST) -> None:
        """Visit and analyze decorator nodes."""
        if isinstance(decorator, ast.Name):
            # Simple decorator like @staticmethod
            pass
        elif isinstance(decorator, ast.Call):
            # Decorator with arguments like @dataclass(frozen=True)
            if isinstance(decorator.func, ast.Name):
                pass
        elif isinstance(decorator, ast.Attribute):
            # Decorator like @pytest.mark.skip
            pass
    
    def visit_Global(self, node: ast.Global) -> None:
        """Track global variable declarations."""
        for name in node.names:
            self.context.global_variables.add(name)
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name) -> None:
        """Track global variable assignments."""
        if isinstance(node.ctx, ast.Store):
            # Check if this might be a global assignment
            if hasattr(node, 'id') and node.id in self.context.global_variables:
                # This is a global variable mutation
                pass
        self.generic_visit(node)
    
    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Handle list comprehensions."""
        self.generic_visit(node)
    
    def visit_SetComp(self, node: ast.SetComp) -> None:
        """Handle set comprehensions."""
        self.generic_visit(node)
    
    def visit_DictComp(self, node: ast.DictComp) -> None:
        """Handle dictionary comprehensions."""
        self.generic_visit(node)
    
    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        """Handle generator expressions."""
        self.generic_visit(node)
    
    def visit_Lambda(self, node: ast.Lambda) -> None:
        """Handle lambda functions."""
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try) -> None:
        """Handle exception handling blocks."""
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Handle exception handlers."""
        self.generic_visit(node)
    
    def visit_With(self, node: ast.With) -> None:
        """Handle context managers."""
        self.generic_visit(node)
    
    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        """Handle async context managers."""
        self.generic_visit(node)


def parse_file(file_path: str) -> Optional[ast.AST]:
    """
    Parse a Python file and return the AST.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        AST object or None if parsing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return ast.parse(content, filename=file_path)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}")
        return None


def build_context(tree: ast.AST) -> AnalysisContext:
    """
    Build analysis context by traversing the AST.
    
    Args:
        tree: The AST to analyze
        
    Returns:
        AnalysisContext with imports, functions, classes, etc.
    """
    visitor = ASTVisitor()
    visitor.visit(tree)
    return visitor.context


def get_function_calls(node: ast.AST) -> List[str]:
    """
    Extract all function calls from an AST node.
    
    Args:
        node: AST node to analyze
        
    Returns:
        List of function call names
    """
    calls = []
    
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.append(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                # Handle method calls like obj.method()
                if isinstance(child.func.value, ast.Name):
                    calls.append(f"{child.func.value.id}.{child.func.attr}")
                elif isinstance(child.func.value, ast.Attribute):
                    # Handle chained method calls like obj.method1.method2()
                    calls.append(_get_chained_attribute_name(child.func.value))
    
    return calls


def _get_chained_attribute_name(node: ast.Attribute) -> str:
    """
    Extract the full name from a chained attribute access.
    
    Args:
        node: Attribute node to analyze
        
    Returns:
        Full attribute name as string
    """
    parts = []
    current = node
    
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    
    if isinstance(current, ast.Name):
        parts.append(current.id)
    
    return ".".join(reversed(parts))


def get_variable_assignments(node: ast.AST) -> List[str]:
    """
    Extract all variable assignments from an AST node.
    
    Args:
        node: AST node to analyze
        
    Returns:
        List of variable names being assigned
    """
    assignments = []
    
    for child in ast.walk(node):
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name):
                    assignments.append(target.id)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            assignments.append(elt.id)
    
    return assignments
