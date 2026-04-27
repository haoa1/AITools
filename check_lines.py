#!/usr/bin/env python3
import sys

with open('stock/stock.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'Failed to get company information' in line:
        print(f'Line {i}: {repr(line)}')
        print(f'Next line {i+1}: {repr(lines[i+1]) if i+1 < len(lines) else None}')
        print(f'Next line {i+2}: {repr(lines[i+2]) if i+2 < len(lines) else None}')
        print(f'Next line {i+3}: {repr(lines[i+3]) if i+3 < len(lines) else None}')
        break