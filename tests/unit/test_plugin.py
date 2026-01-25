# SPDX-FileCopyrightText: Copyright (c) 2025-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

# flake8: noqa: WPS433

import ast
from typing import Callable

try:
    from typing import TypeAlias  # type: ignore [attr-defined, unused-ignore]
except ImportError:
    from typing_extensions import TypeAlias  # noqa: WPS440

import pytest

from flake8_code_free_tests.plugin import Plugin

_PLUGIN_RUN_T: TypeAlias = Callable[
    [str], list[tuple[int, int, str]],
]


@pytest.fixture
def plugin_run() -> _PLUGIN_RUN_T:
    """Fixture for easy run plugin."""
    def _plugin_run(code: str) -> list[tuple[int, int, str]]:  # noqa: WPS430
        """Plugin run result."""
        plugin = Plugin(ast.parse(code))
        res = []
        for viol in plugin.run():
            res.append((
                viol[0],
                viol[1],
                viol[2],
            ))
        return res
    return _plugin_run


@pytest.mark.parametrize('decorator', [
    '@pytest.fixture',
    '@pytest.fixture()',
    '@fixture',
    '@fixture()',
])
def test_fixture_loop(plugin_run: _PLUGIN_RUN_T, decorator: str) -> None:
    """Test fixture loop."""
    got = plugin_run('\n'.join([
        decorator,
        'def test_fixture_loop():',
        '    res = []',
        '    for item in items:',
        '        res.append(item)',
        '    return res',
    ]))

    assert not got


def test_valid_test_function(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test valid test function without control flow."""
    got = plugin_run('\n'.join([
        'def test_simple():',
        '    assert True',
        '',
        'def test_with_assertions():',
        '    result = some_function()',
        '    assert result == expected',
        '    assert result is not None',
    ]))

    assert not got


def test_test_function_with_if(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with if statement."""
    got = plugin_run('\n'.join([
        'def test_with_if():',
        '    if some_condition:',
        '        assert True',
        '    else:',
        '        assert False',
    ]))

    assert got == [
        (2, 4, 'CFT110 test functions should not contain if statements'),
    ]


def test_test_function_with_for_loop(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with for loop."""
    got = plugin_run('\n'.join([
        'def test_with_for():',
        '    for item in items:',
        '        assert item is not None',
    ]))

    assert got == [
        (2, 4, 'CFT120 test functions should not contain for loops'),
    ]


def test_test_function_with_while_loop(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with while loop."""
    got = plugin_run('\n'.join([
        'def test_with_while():',
        '    while condition:',
        '        assert True',
    ]))

    assert got == [
        (2, 4, 'CFT130 test functions should not contain while loops'),
    ]


def test_test_function_with_try_except(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with try/except."""
    got = plugin_run('\n'.join([
        'def test_with_try():',
        '    try:',
        '        risky_operation()',
        '    except Exception:',
        '        assert False',
    ]))

    assert got == [
        (2, 4, 'CFT140 test functions should not contain try/except blocks'),
    ]


def test_test_function_with_with_statement(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with with statement."""
    got = plugin_run('\n'.join([
        'def test_with_with():',
        '    with open("file.txt") as f:',
        '        assert f is not None',
    ]))

    assert got == [
        (2, 4, 'CFT150 test functions should not contain with statements'),
    ]


def test_test_function_with_list_comprehension(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with list comprehension."""
    got = plugin_run('\n'.join([
        'def test_with_list_comp():',
        '    result = [x for x in range(10)]',
        '    assert len(result) == 10',
    ]))

    assert got == [
        (2, 13, 'CFT210 test functions should not contain list comprehensions'),
    ]


def test_test_function_with_dict_comprehension(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with dict comprehension."""
    got = plugin_run('\n'.join([
        'def test_with_dict_comp():',
        '    result = {x: x*2 for x in range(5)}',
        '    assert len(result) == 5',
    ]))

    assert got == [
        (2, 13, 'CFT220 test functions should not contain dict comprehensions'),
    ]


def test_test_function_with_set_comprehension(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with set comprehension."""
    got = plugin_run('\n'.join([
        'def test_with_set_comp():',
        '    result = {x for x in range(5)}',
        '    assert len(result) == 5',
    ]))

    assert got == [
        (2, 13, 'CFT230 test functions should not contain set comprehensions'),
    ]


def test_test_function_with_generator_expression(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with generator expression."""
    got = plugin_run('\n'.join([
        'def test_with_gen_exp():',
        '    result = (x for x in range(5))',
        '    assert sum(result) == 10',
    ]))

    assert got == [
        (2, 13, 'CFT240 test functions should not contain generator comprehensions'),
    ]


def test_non_test_function_allowed(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test that non-test functions can contain control flow."""
    got = plugin_run('\n'.join([
        'def regular_function():',
        '    if condition:',
        '        return True',
        '    for item in items:',
        '        process(item)',
        '    return False',
    ]))

    assert not got


def test_pytest_decorated_function(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test function decorated with pytest.mark."""
    got = plugin_run('\n'.join([
        'import pytest',
        '',
        '@pytest.mark.parametrize("value", [1, 2, 3])',
        'def test_parametrized(value):',
        '    if value > 2:',
        '        assert True',
    ]))

    assert got == [
        (5, 4, 'CFT110 test functions should not contain if statements'),
    ]


def test_async_test_function(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test async test function."""
    got = plugin_run('\n'.join([
        'async def test_async():',
        '    if condition:',
        '        assert True',
    ]))

    assert got == [
        (2, 4, 'CFT110 test functions should not contain if statements'),
    ]


def test_multiple_violations(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test test function with multiple control flow violations."""
    got = plugin_run('\n'.join([
        'def test_multiple_violations():',
        '    if condition:',
        '        for item in items:',
        '            while True:',
        '                try:',
        '                    with open("file"):',
        '                        pass',
        '                except:',
        '                    pass',
    ]))

    assert len(got) == 5  # if, for, while, try, with
    assert any('CFT110' in msg for _, _, msg in got)  # if
    assert any('CFT120' in msg for _, _, msg in got)  # for
    assert any('CFT130' in msg for _, _, msg in got)  # while
    assert any('CFT140' in msg for _, _, msg in got)  # try
    assert any('CFT150' in msg for _, _, msg in got)  # with


def test_unittest_testcase_with_if(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test unittest TestCase with if statement."""
    got = plugin_run('\n'.join([
        'import unittest',
        '',
        'class TestExample(unittest.TestCase):',
        '',
        '    def test_with_if(self):',
        '        if condition:',
        '            self.assertTrue(True)',
        '        else:',
        '            self.assertFalse(False)',
    ]))

    assert got == [
        (6, 8, 'CFT110 test functions should not contain if statements'),
    ]


def test_unittest_testcase_with_for(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test unittest TestCase with for loop."""
    got = plugin_run('\n'.join([
        'import unittest',
        '',
        'class TestExample(unittest.TestCase):',
        '',
        '    def test_with_for(self):',
        '        for item in items:',
        '            self.assertIsNotNone(item)',
    ]))

    assert got == [
        (6, 8, 'CFT120 test functions should not contain for loops'),
    ]


def test_unittest_testcase_with_while(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test unittest TestCase with while loop."""
    got = plugin_run('\n'.join([
        'import unittest',
        '',
        'class TestExample(unittest.TestCase):',
        '',
        '    def test_with_while(self):',
        '        while condition:',
        '            self.assertTrue(True)',
    ]))

    assert got == [
        (6, 8, 'CFT130 test functions should not contain while loops'),
    ]


def test_unittest_testcase_with_try(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test unittest TestCase with try/except."""
    got = plugin_run('\n'.join([
        'import unittest',
        '',
        'class TestExample(unittest.TestCase):',
        '',
        '    def test_with_try(self):',
        '        try:',
        '            risky_operation()',
        '        except Exception:',
        '            self.fail("Should not raise")',
    ]))

    assert got == [
        (6, 8, 'CFT140 test functions should not contain try/except blocks'),
    ]


def test_unittest_testcase_valid(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test valid unittest TestCase without control flow."""
    got = plugin_run('\n'.join([
        'import unittest',
        '',
        'class TestExample(unittest.TestCase):',
        '',
        '    def test_simple(self):',
        '        result = some_function()',
        '        self.assertIsNotNone(result)',
        '        self.assertEqual(result, expected)',
        '',
        '    def test_another(self):',
        '        self.assertTrue(True)',
        '        self.assertFalse(False)',
    ]))

    assert not got


def test_unittest_testcase_non_test_method(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test that non-test methods in TestCase can contain control flow."""
    got = plugin_run('\n'.join([
        'import unittest',
        '',
        'class TestExample(unittest.TestCase):',
        '',
        '    def setUp(self):',
        '        if condition:',
        '            self.data = "test"',
        '        for item in items:',
        '            self.process(item)',
        '',
        '    def tearDown(self):',
        '        while self.has_data:',
        '            self.cleanup()',
        '',
        '    def test_simple(self):',
        '        self.assertTrue(True)',
    ]))

    assert not got


def test_unittest_testcase_import_variations(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test unittest TestCase with different import styles."""
    got = plugin_run('\n'.join([
        'from unittest import TestCase',
        '',
        'class TestExample(TestCase):',
        '',
        '    def test_with_if(self):',
        '        if condition:',
        '            self.assertTrue(True)',
    ]))

    assert got == [
        (6, 8, 'CFT110 test functions should not contain if statements'),
    ]


def test_unittest_testcase_multiple_violations(plugin_run: _PLUGIN_RUN_T) -> None:
    """Test unittest TestCase with multiple control flow violations."""
    got = plugin_run('\n'.join([
        'import unittest',
        '',
        'class TestExample(unittest.TestCase):',
        '',
        '    def test_multiple_violations(self):',
        '        if condition:',
        '            for item in items:',
        '                while True:',
        '                    try:',
        '                        pass',
        '                    except:',
        '                        pass',
    ]))

    assert len(got) == 4  # if, for, while, try
    assert 'CFT110' in got[0][2]  # if
    assert 'CFT120' in got[1][2]  # for
    assert 'CFT130' in got[2][2]  # while
    assert 'CFT140' in got[3][2]  # try
