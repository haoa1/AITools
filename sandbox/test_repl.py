#!/usr/bin/env python3
"""Simple test REPL for Windows sandbox testing.
Reads lines from stdin, echoes back with PROMPT marker."""
import sys

print("REPL_READY", flush=True)
print("PROMPT>", end="", flush=True)

while True:
    try:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.rstrip('\n\r')
        if line == "__EXIT__":
            break
        print(f"ECHO: {line}", flush=True)
        print("PROMPT>", end="", flush=True)
    except EOFError:
        break
    except:
        break
