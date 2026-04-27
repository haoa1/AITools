#!/usr/bin/env python3
"""Simple echo server for interactive sandbox testing"""
import sys

PROMPT = "ECHO> "

def main():
    print("ECHO_READY", flush=True)
    print(PROMPT, end="", flush=True)
    for line in sys.stdin:
        line = line.strip()
        if line == "quit" or line == "exit":
            print("ECHO: bye", flush=True)
            break
        print(f"ECHO: {line}", flush=True)
        print(PROMPT, end="", flush=True)

if __name__ == "__main__":
    main()
