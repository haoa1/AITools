#!/usr/bin/env python3
"""Scan all tool modules for Windows import compatibility."""
import sys, os, importlib, traceback

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

# All tool modules to test
modules = [
    "shell.bash",
    "shell.power_shell_tool",
    "interaction.interaction",
    "interaction.notification_tool",
    "interaction.enhanced_interaction",
    "interaction.repl_tool",
    "interaction.send_message_tool",
    "interaction.input_helper",
    "file.file_read_tool",
    "file.write",
    "file.delete",
    "file.replace",
    "compress.compress",
    "git.git",
    "docker.docker",
    "system.agent_tool",
    "system.config_tool",
    "system.ctx_inspect_tool",
    "system.enter_plan_mode_tool",
    "system.enter_worktree_tool",
    "system.exit_plan_mode_tool",
    "system.exit_worktree_tool",
    "system.finish",
    "system.monitor",
    "system.sleep",
    "system.snip_tool",
    "system.system_info_tool",
    "system.task_create_tool",
    "system.task_get_tool",
    "system.task_list_tool",
    "system.task_manager",
    "system.task_output_tool",
    "system.task_stop",
    "system.todo_write_tool",
    "system.tool_search_tool",
    "system.terminal_capture_tool",
    "network.list_mcp_resources_tool",
    "network.read_mcp_resource_tool",
    "web_search.web_search",
    "database.database",
    "diagram.diagram",
    "pdf.pdf",
    "markdown.markdown",
    "stock.stock",
    "summary.summary",
    "workspace.workspace",
    "tmux.tmux",
    "sandbox.sandbox",
    "architect.architect",
    "memory.memory_recall",
    "system.synthetic_output_tool",
    "system.overflow_test_tool",
]

PASS = []
MODULE_ERRORS = []
IMPORT_ERRORS = []

for mod_name in modules:
    try:
        importlib.import_module(mod_name)
        PASS.append(mod_name)
        print(f"  OK: {mod_name}")
    except ModuleNotFoundError as e:
        IMPORT_ERRORS.append((mod_name, str(e)))
        print(f"  ?? {mod_name}: ModuleNotFoundError - {e}")
    except Exception as e:
        MODULE_ERRORS.append((mod_name, traceback.format_exc()))
        print(f"  !! {mod_name}: {type(e).__name__}: {e}")

print(f"\n====== 导入结果 ======")
print(f"  成功: {len(PASS)}")
print(f"  模块缺失: {len(IMPORT_ERRORS)}")
print(f"  导入异常: {len(MODULE_ERRORS)}")

if IMPORT_ERRORS:
    print(f"\n--- 模块缺失 ---")
    for name, err in IMPORT_ERRORS:
        print(f"  {name}: {err}")

if MODULE_ERRORS:
    print(f"\n--- 导入异常详情 ---")
    for name, tb in MODULE_ERRORS:
        print(f"\n  === {name} ===")
        # Only show last few lines of traceback
        lines = tb.strip().split("\n")
        for line in lines[-5:]:
            print(f"    {line}")

sys.exit(1 if MODULE_ERRORS else 0)
