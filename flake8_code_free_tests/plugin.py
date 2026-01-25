# SPDX-FileCopyrightText: Copyright (c) 2025-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

# flake8: noqa: WPS232

import ast
from collections.abc import Generator
from typing import final


@final
class TestControlFlowVisitor(ast.NodeVisitor):
    """Visitor for checking that test functions don't contain control flow statements."""

    def __init__(self) -> None:
        """Ctor."""
        self.problems: list[tuple[int, int, str]] = []
        self._in_test_function = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        """Visit function definitions."""
        self._check_if_test_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        """Visit async function definitions."""
        self._check_if_test_function(node)
        self.generic_visit(node)

    def _check_if_test_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check if function is a test function and set flag."""
        # Check if function name starts with 'test_' but exclude fixtures
        is_test_function = (
            node.name.startswith('test_') and
            not self._is_fixture(node)
        )
        
        if is_test_function:
            self._in_test_function = True
            self.generic_visit(node)
            self._in_test_function = False
        else:
            self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        """Visit class definitions to check for unittest test methods."""
        # Check if this is a unittest TestCase class
        is_test_case = self._is_unittest_testcase(node)
        
        if is_test_case:
            # Visit all methods in the TestCase class
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith('test_'):
                        self._in_test_function = True
                        self.generic_visit(item)
                        self._in_test_function = False
                    else:
                        self.generic_visit(item)
                else:
                    self.generic_visit(item)
        else:
            self.generic_visit(node)

    def _is_unittest_testcase(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from unittest.TestCase."""
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in {'TestCase', 'unittest'}:
                    return True
            elif isinstance(base, ast.Attribute):
                if (
                    isinstance(base.value, ast.Name) and
                    base.value.id == 'unittest' and
                    base.attr == 'TestCase'
                ):
                    return True
        return False

    def _is_fixture(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if function is a pytest fixture."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in {'fixture', 'pytest'}:
                    return True
            elif isinstance(decorator, ast.Attribute):
                if (
                    isinstance(decorator.value, ast.Name) and
                    decorator.value.id == 'pytest' and
                    decorator.attr == 'fixture'
                ):
                    return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id in {'fixture', 'pytest'}:
                        return True
                elif isinstance(decorator.func, ast.Attribute):
                    if (
                        isinstance(decorator.func.value, ast.Name) and
                        decorator.func.value.id == 'pytest' and
                        decorator.func.attr == 'fixture'
                    ):
                        return True
        return False

    def visit_If(self, node: ast.If) -> None:  # noqa: N802
        """Visit if statements."""
        if self._in_test_function:
            self.problems.append((
                node.lineno, 
                node.col_offset, 
                'CFT001 test functions should not contain if statements'
            ))
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        """Visit for loops."""
        if self._in_test_function:
            self.problems.append((
                node.lineno, 
                node.col_offset, 
                'CFT002 test functions should not contain for loops'
            ))
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:  # noqa: N802
        """Visit while loops."""
        if self._in_test_function:
            self.problems.append((
                node.lineno, 
                node.col_offset, 
                'CFT003 test functions should not contain while loops'
            ))
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:  # noqa: N802
        """Visit try statements."""
        if self._in_test_function:
            self.problems.append((
                node.lineno, 
                node.col_offset, 
                'CFT004 test functions should not contain try/except blocks'
            ))
        self.generic_visit(node)


@final
class Plugin:
    """Flake8 plugin."""

    def __init__(self, tree: ast.AST) -> None:
        """Ctor."""
        self._tree = tree

    def run(self) -> Generator[tuple[int, int, str, type], None, None]:
        """Entry."""
        visitor = TestControlFlowVisitor()
        visitor.visit(self._tree)
        for line, col, message in visitor.problems:  # noqa: WPS526
            yield (line, col, message, type(self))
