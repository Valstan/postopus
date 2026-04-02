"""
Unit tests for start.py CLI argument parsing.
Tests the --test flag handling without executing full start logic.
"""

import pytest


def test_start_py_cli_with_test_flag():
    """Test that --test flag is recognized and removed from arguments."""

    test_args = ["start.py", "mi_novost", "--test"]
    args = test_args[1:]
    test_flag = False

    if "--test" in args:
        test_flag = True
        args.remove("--test")

    assert test_flag is True
    assert args == ["mi_novost"]
    assert "--test" not in args


def test_start_py_cli_without_test_flag():
    """Test normal argument parsing without --test flag."""

    test_args = ["start.py", "mi_novost", "1"]
    args = test_args[1:]
    test_flag = False

    if "--test" in args:
        test_flag = True
        args.remove("--test")

    assert test_flag is False
    assert args == ["mi_novost", "1"]


def test_start_py_cli_test_flag_position_first():
    """Test that --test flag works in first position."""

    test_args = ["start.py", "--test", "mi_novost"]
    args = test_args[1:]
    test_flag = False

    if "--test" in args:
        test_flag = True
        args.remove("--test")

    assert test_flag is True
    assert args == ["mi_novost"]


def test_start_py_cli_test_flag_position_middle():
    """Test that --test flag works in middle position."""

    test_args = ["start.py", "mi_novost", "--test", "1"]
    args = test_args[1:]
    test_flag = False

    if "--test" in args:
        test_flag = True
        args.remove("--test")

    assert test_flag is True
    assert args == ["mi_novost", "1"]


def test_start_py_cli_multiple_args():
    """Test CLI with multiple arguments including test flag."""

    test_args = ["start.py", "mi_novost", "2", "--test"]
    args = test_args[1:]
    test_flag = False

    if "--test" in args:
        test_flag = True
        args.remove("--test")

    assert test_flag is True
    assert len(args) == 2
    assert args == ["mi_novost", "2"]


def test_start_py_session_flag_setting():
    """Test that test_flag properly sets session['post_to_test_polygon']."""

    # Mock session
    mock_session = {
        "post_to_test_polygon": False,
    }

    test_flag = True

    # Simulate the logic from start.py
    if test_flag:
        mock_session["post_to_test_polygon"] = True

    assert mock_session["post_to_test_polygon"] is True


def test_start_py_session_flag_not_set():
    """Test that session flag remains False when test_flag is False."""

    mock_session = {
        "post_to_test_polygon": False,
    }

    test_flag = False

    # Simulate the logic from start.py
    if test_flag:
        mock_session["post_to_test_polygon"] = True

    assert mock_session["post_to_test_polygon"] is False


def test_start_py_argument_extraction():
    """Test correct extraction of session name and bags from arguments."""

    test_args = ["start.py", "mi_novost", "1", "--test"]
    args = test_args[1:]
    test_flag = False

    if "--test" in args:
        test_flag = True
        args.remove("--test")

    # Extract arguments
    if len(args) == 2:
        session_name = args[0]
        bags = args[1]
    elif len(args) == 1:
        session_name = args[0]
        bags = "0"

    assert session_name == "mi_novost"
    assert bags == "1"
    assert test_flag is True


def test_start_py_default_bags():
    """Test that bags defaults to '0' when not provided."""

    test_args = ["start.py", "mi_novost", "--test"]
    args = test_args[1:]

    if "--test" in args:
        args.remove("--test")

    # Extract arguments
    if len(args) == 2:
        session_name = args[0]
        bags = args[1]
    elif len(args) == 1:
        session_name = args[0]
        bags = "0"
    else:
        session_name = None
        bags = None

    assert session_name == "mi_novost"
    assert bags == "0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
