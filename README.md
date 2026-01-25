# flake8-code-free-tests

[![Build Status](https://github.com/blablatdinov/flake8-code-free-tests/workflows/test/badge.svg?branch=master&event=push)](https://github.com/blablatdinov/flake8-code-free-tests/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/blablatdinov/flake8-code-free-tests/branch/master/graph/badge.svg)](https://codecov.io/gh/blablatdinov/flake8-code-free-tests)
[![Python Version](https://img.shields.io/pypi/pyversions/flake8-code-free-tests.svg)](https://pypi.org/project/flake8-code-free-tests/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

`flake8-code-free-tests` is a Flake8 plugin designed to enforce control-flow-free test functions. This plugin ensures that test functions don't contain complex control flow statements like `if`, `for`, `while`, `try/except`, statements, and comprehensions, promoting simpler, more focused, and easier-to-understand tests.

The plugin follows the principle that tests should be simple, linear, and focused on a single behavior, making them easier to read, maintain, and debug.

## Installation

You can install flake8-code-free-tests via pip:

```bash
pip install flake8-code-free-tests
```

## Usage

To use flake8-code-free-tests, simply include it in your Flake8 configuration. You can run Flake8 as usual, and the plugin will check for the presence of the @override decorator on each method.

```bash
flake8 your_code_directory
```

## Example

### Input code (violations)

```python
def test_user_creation():
    if user_exists:
        for user in users:
            while not user.is_valid:
                try:
                    with open('config.json') as f:
                        user = create_user(f.read())
                except Exception:
                    assert False
    assert user is not None
```

### Expected code (no violations)

```python
def test_user_creation():
    user = create_user('{"name": "test"}')
    assert user is not None
    assert user.name == "test"
    assert user.is_valid is True
```

## Error Codes

The plugin reports the following error codes:

- `CFT110`: test functions should not contain if statements
- `CFT120`: test functions should not contain for loops
- `CFT130`: test functions should not contain while loops
- `CFT140`: test functions should not contain try/except blocks
- `CFT150`: test functions should not contain with statements
- `CFT210`: test functions should not contain list comprehensions
- `CFT220`: test functions should not contain dict comprehensions
- `CFT230`: test functions should not contain set comprehensions
- `CFT240`: test functions should not contain generator comprehensions


## Rationale

The primary motivation for this plugin is to enforce simple, linear test functions that are:

- **Easier to Read**: Linear tests without complex control flow are easier to understand at a glance
- **Easier to Debug**: When a test fails, there's only one path through the code to analyze
- **More Focused**: Each test function tests exactly one behavior or scenario
- **Less Error-Prone**: Simple tests are less likely to contain bugs themselves
- **Better for TDD**: Forces developers to write focused, single-purpose tests

This approach aligns with the principle that tests should be simple, predictable, and focused on verifying specific behaviors rather than implementing complex logic.

## License

[MIT](https://github.com/blablatdinov/flake8-code-free-tests/blob/master/LICENSE)

## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [864a62ecb432655249d071e263ac51f053448659](https://github.com/wemake-services/wemake-python-package/tree/864a62ecb432655249d071e263ac51f053448659). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/864a62ecb432655249d071e263ac51f053448659...master) since then.
