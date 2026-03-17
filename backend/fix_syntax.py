#!/usr/bin/env python3
# Fix syntax errors in train.py

with open('train.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 28 - replace escaped quotes with regular quotes
fixed_lines = []
for i, line in enumerate(lines, 1):
    if i == 28:
        # Replace the escaped quotes
        line = line.replace('print(f\\"', 'print(f"')
        line = line.replace('\\")', '")')
    fixed_lines.append(line)

with open('train.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed syntax errors in train.py")
