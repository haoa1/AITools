#!/usr/bin/env python3
"""
Test suite for shell/bash.py functions.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shell.bash import (
    execute_command,
    check_command_exists,
    execute_multiple_commands,
    get_process_info,
    get_system_info
)

def test_execute_command_basic():
    """Test basic command execution."""
    print("Testing execute_command with simple echo...")
    result = execute_command("echo hello", capture_output=True)
    assert "hello" in result, f"Expected 'hello' in output, got: {result}"
    print("✓ Basic command execution works")

def test_execute_command_capture_output_false():
    """Test command execution without capturing output."""
    print("Testing execute_command with capture_output=False...")
    result = execute_command("echo hidden", capture_output=False)
    # Should return a message about return code
    assert "return code" in result.lower() or "executed" in result.lower(), \
        f"Expected return code message, got: {result}"
    print("✓ No capture output works")

def test_execute_command_working_dir():
    """Test command execution with working directory."""
    print("Testing execute_command with working directory...")
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = execute_command("pwd", working_dir=tmpdir, capture_output=True)
        assert tmpdir in result, f"Expected {tmpdir} in output, got: {result}"
    print("✓ Working directory works")

def test_execute_command_timeout():
    """Test command timeout handling."""
    print("Testing execute_command timeout...")
    # Use sleep command that exceeds timeout
    result = execute_command("sleep 2", timeout=1, capture_output=True)
    # Should show timeout error
    assert "timeout" in result.lower() or "timed out" in result.lower(), \
        f"Expected timeout message, got: {result}"
    print("✓ Timeout handling works")

def test_execute_command_env_vars():
    """Test command with environment variables."""
    print("Testing execute_command with env_vars...")
    result = execute_command("echo $MYVAR", env_vars={"MYVAR": "testvalue"}, capture_output=True)
    assert "testvalue" in result, f"Expected 'testvalue' in output, got: {result}"
    print("✓ Environment variables work")

def test_check_command_exists():
    """Test checking command existence."""
    print("Testing check_command_exists...")
    # Test with existing command
    result = check_command_exists("ls")
    assert "exists" in result.lower(), f"Expected 'exists' in result, got: {result}"
    
    # Test with non-existent command
    result = check_command_exists("nonexistentcommandxyz123")
    assert "not found" in result.lower() or "not exist" in result.lower(), \
        f"Expected 'not found' in result, got: {result}"
    print("✓ Command existence check works")

def test_execute_multiple_commands():
    """Test executing multiple commands."""
    print("Testing execute_multiple_commands...")
    commands = "echo first; echo second"
    result = execute_multiple_commands(commands, capture_output=True)
    assert "first" in result and "second" in result, \
        f"Expected both outputs, got: {result}"
    print("✓ Multiple commands execution works")

def test_get_process_info():
    """Test getting process information."""
    print("Testing get_process_info...")
    # Get info about current process (python)
    result = get_process_info("python")
    # Should contain process information
    assert result and len(result) > 0, "Expected process info, got empty result"
    print("✓ Process info retrieval works")

def test_get_system_info():
    """Test getting system information."""
    print("Testing get_system_info...")
    result = get_system_info()
    # Should contain system info headers
    assert "System Information" in result, \
        f"Expected 'System Information' in result, got: {result}"
    print("✓ System info retrieval works")

def run_all_tests():
    """Run all test functions."""
    tests = [
        test_execute_command_basic,
        test_execute_command_capture_output_false,
        test_execute_command_working_dir,
        test_execute_command_timeout,
        test_execute_command_env_vars,
        test_check_command_exists,
        test_execute_multiple_commands,
        test_get_process_info,
        test_get_system_info,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"✗ {test_func.__name__} failed: {e}")
        except Exception as e:
            failed += 1
            print(f"✗ {test_func.__name__} raised exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Summary: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()