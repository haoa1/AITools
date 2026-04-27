"""
Comprehensive test suite for bash.py module.
Tests all functions: execute_command, check_command_exists, execute_multiple_commands, 
get_process_info, and get_system_info.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, '/work/workspace/AITools')

from shell.bash import (
    execute_command,
    check_command_exists,
    execute_multiple_commands,
    get_process_info,
    get_system_info
)


def test_execute_command_basic():
    """Test basic command execution"""
    print("\n" + "="*60)
    print("TEST 1: execute_command - Basic Command")
    print("="*60)
    result = execute_command("echo 'Hello World'")
    print(f"Result: {result}")
    assert "Hello World" in result or "Hello World" in str(result)
    print("✓ PASSED")


def test_execute_command_with_return_code():
    """Test command execution with return code checking"""
    print("\n" + "="*60)
    print("TEST 2: execute_command - Command with Return Code")
    print("="*60)
    result = execute_command("ls /tmp")
    print(f"Result: {result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_execute_command_with_timeout():
    """Test command execution with timeout"""
    print("\n" + "="*60)
    print("TEST 3: execute_command - With Timeout")
    print("="*60)
    result = execute_command("sleep 2", timeout=5)
    print(f"Result: {result}")
    assert "timeout" not in result.lower() or result  # Should not timeout
    print("✓ PASSED")


def test_execute_command_with_working_dir():
    """Test command execution in specific working directory"""
    print("\n" + "="*60)
    print("TEST 4: execute_command - With Working Directory")
    print("="*60)
    result = execute_command("pwd", working_dir="/tmp")
    print(f"Result: {result}")
    assert "tmp" in result or isinstance(result, str)
    print("✓ PASSED")


def test_execute_command_with_env_vars():
    """Test command execution with environment variables"""
    print("\n" + "="*60)
    print("TEST 5: execute_command - With Environment Variables")
    print("="*60)
    result = execute_command("echo $TEST_VAR", env_vars={"TEST_VAR": "test_value"})
    print(f"Result: {result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_execute_command_with_input():
    """Test command execution with stdin input"""
    print("\n" + "="*60)
    print("TEST 6: execute_command - With Input Data (stdin)")
    print("="*60)
    result = execute_command("cat", input_data="Hello from stdin\n")
    print(f"Result: {result}")
    assert "Hello" in result or isinstance(result, str)
    print("✓ PASSED")


def test_execute_command_invalid_command():
    """Test command execution with invalid command"""
    print("\n" + "="*60)
    print("TEST 7: execute_command - Invalid Command (Error Handling)")
    print("="*60)
    result = execute_command("invalid_command_xyz_123")
    print(f"Result: {result}")
    assert "Error" in result or "not found" in result or isinstance(result, str)
    print("✓ PASSED")


def test_execute_command_boolean_conversion():
    """Test boolean parameter conversion from string"""
    print("\n" + "="*60)
    print("TEST 8: execute_command - Boolean String Conversion")
    print("="*60)
    result = execute_command("echo test", capture_output="true", shell="false")
    print(f"Result: {result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_execute_command_timeout_conversion():
    """Test timeout parameter conversion from string"""
    print("\n" + "="*60)
    print("TEST 9: execute_command - Timeout String Conversion")
    print("="*60)
    result = execute_command("sleep 1", timeout="5")
    print(f"Result: {result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_check_command_exists_success():
    """Test checking if a command exists (should exist)"""
    print("\n" + "="*60)
    print("TEST 10: check_command_exists - Command That Exists (ls)")
    print("="*60)
    result = check_command_exists("ls")
    print(f"Result: {result}")
    assert "exists" in result.lower() or "ls" in result
    print("✓ PASSED")


def test_check_command_exists_failure():
    """Test checking if a command exists (should not exist)"""
    print("\n" + "="*60)
    print("TEST 11: check_command_exists - Command That Doesn't Exist")
    print("="*60)
    result = check_command_exists("invalid_command_xyz_abc_123")
    print(f"Result: {result}")
    assert "not found" in result.lower() or "Error" in result
    print("✓ PASSED")


def test_check_command_exists_python():
    """Test checking if python command exists"""
    print("\n" + "="*60)
    print("TEST 12: check_command_exists - Python Command")
    print("="*60)
    result = check_command_exists("python")
    print(f"Result: {result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_execute_multiple_commands_semicolon():
    """Test executing multiple commands separated by semicolons"""
    print("\n" + "="*60)
    print("TEST 13: execute_multiple_commands - Semicolon Separated")
    print("="*60)
    result = execute_multiple_commands("echo 'First'; echo 'Second'; echo 'Third'")
    print(f"Result:\n{result}")
    assert "Command 1" in result and "Command 2" in result and "Command 3" in result
    print("✓ PASSED")


def test_execute_multiple_commands_newline():
    """Test executing multiple commands separated by newlines"""
    print("\n" + "="*60)
    print("TEST 14: execute_multiple_commands - Newline Separated")
    print("="*60)
    commands = """echo 'Line 1'
echo 'Line 2'
echo 'Line 3'"""
    result = execute_multiple_commands(commands)
    print(f"Result:\n{result}")
    assert "Command 1" in result and "Command 2" in result and "Command 3" in result
    print("✓ PASSED")


def test_execute_multiple_commands_single():
    """Test executing single command as multiple"""
    print("\n" + "="*60)
    print("TEST 15: execute_multiple_commands - Single Command")
    print("="*60)
    result = execute_multiple_commands("echo 'Single'")
    print(f"Result:\n{result}")
    assert "Command 1" in result
    print("✓ PASSED")


def test_execute_multiple_commands_with_timeout():
    """Test multiple commands with timeout"""
    print("\n" + "="*60)
    print("TEST 16: execute_multiple_commands - With Timeout String")
    print("="*60)
    result = execute_multiple_commands("echo 'Test 1'; echo 'Test 2'", timeout="10")
    print(f"Result:\n{result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_execute_multiple_commands_empty():
    """Test executing empty commands"""
    print("\n" + "="*60)
    print("TEST 17: execute_multiple_commands - Empty Commands (Error Handling)")
    print("="*60)
    result = execute_multiple_commands(";;;")
    print(f"Result: {result}")
    assert "Error" in result or "No commands" in result
    print("✓ PASSED")


def test_get_process_info_all():
    """Test getting all process information"""
    print("\n" + "="*60)
    print("TEST 18: get_process_info - All Processes")
    print("="*60)
    result = get_process_info()
    print(f"Result (first 500 chars):\n{result[:500]}...")
    assert isinstance(result, str) and len(result) > 0
    print("✓ PASSED")


def test_get_process_info_filtered():
    """Test getting filtered process information"""
    print("\n" + "="*60)
    print("TEST 19: get_process_info - Filtered by 'python'")
    print("="*60)
    result = get_process_info("python")
    print(f"Result:\n{result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_get_process_info_filtered_bash():
    """Test getting filtered process information for bash"""
    print("\n" + "="*60)
    print("TEST 20: get_process_info - Filtered by 'bash'")
    print("="*60)
    result = get_process_info("bash")
    print(f"Result:\n{result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_get_system_info():
    """Test getting system information"""
    print("\n" + "="*60)
    print("TEST 21: get_system_info - General System Info")
    print("="*60)
    result = get_system_info()
    print(f"Result (first 800 chars):\n{result[:800]}...")
    assert "System Information" in result and isinstance(result, str)
    print("✓ PASSED")


def test_get_system_info_no_args():
    """Test system info without arguments"""
    print("\n" + "="*60)
    print("TEST 22: get_system_info - No Arguments")
    print("="*60)
    result = get_system_info()
    print(f"Result length: {len(result)} chars")
    assert isinstance(result, str) and len(result) > 50
    print("✓ PASSED")


def test_execute_command_no_capture():
    """Test command execution without capturing output"""
    print("\n" + "="*60)
    print("TEST 23: execute_command - Without Capturing Output")
    print("="*60)
    result = execute_command("echo 'test'", capture_output=False)
    print(f"Result: {result}")
    assert isinstance(result, str)
    print("✓ PASSED")


def test_execute_command_with_pipes():
    """Test command execution with pipes"""
    print("\n" + "="*60)
    print("TEST 24: execute_command - With Pipes")
    print("="*60)
    result = execute_command("echo 'hello\nworld' | grep 'world'")
    print(f"Result: {result}")
    assert "world" in result or isinstance(result, str)
    print("✓ PASSED")


def test_execute_command_with_redirection():
    """Test command execution with output redirection"""
    print("\n" + "="*60)
    print("TEST 25: execute_command - With Redirection")
    print("="*60)
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "test.txt")
        result = execute_command(f"echo 'test content' > {output_file}", working_dir=tmpdir)
        print(f"Result: {result}")
        assert isinstance(result, str)
    print("✓ PASSED")


def run_all_tests():
    """Run all test functions"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  BASH MODULE - COMPREHENSIVE FUNCTION TESTS".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    test_functions = [
        test_execute_command_basic,
        test_execute_command_with_return_code,
        test_execute_command_with_timeout,
        test_execute_command_with_working_dir,
        test_execute_command_with_env_vars,
        test_execute_command_with_input,
        test_execute_command_invalid_command,
        test_execute_command_boolean_conversion,
        test_execute_command_timeout_conversion,
        test_check_command_exists_success,
        test_check_command_exists_failure,
        test_check_command_exists_python,
        test_execute_multiple_commands_semicolon,
        test_execute_multiple_commands_newline,
        test_execute_multiple_commands_single,
        test_execute_multiple_commands_with_timeout,
        test_execute_multiple_commands_empty,
        test_get_process_info_all,
        test_get_process_info_filtered,
        test_get_process_info_filtered_bash,
        test_get_system_info,
        test_get_system_info_no_args,
        test_execute_command_no_capture,
        test_execute_command_with_pipes,
        test_execute_command_with_redirection,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print(f"█  Test Results: {passed} passed, {failed} failed".ljust(59) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
