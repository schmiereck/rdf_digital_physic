#!/usr/bin/env python3
"""Print lines 320 to 350 of src/new_fitness.py"""
import sys

def main():
    start_line = 320
    end_line = 350
    filepath = "src/new_fitness.py"
    output_file = "output.txt"
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        header = f"Lines {start_line} to {end_line} of {filepath}\n"
        header += "=" * 80 + "\n"
        
        output = []
        for i in range(start_line - 1, min(end_line, len(lines))):
            output.append(f"{i + 1:4d}: {lines[i]}")
        
        if end_line > len(lines):
            output.append(f"\n... (file has {len(lines)} lines, requested up to {end_line})")
        
        output.append("=" * 80)
        
        # Write to file for reliable display
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(header + ''.join(output))
        
        # Also try to print to stdout with replacement
        sys.stdout.reconfigure(errors='replace')
        print(header + ''.join(output))
        print(f"\n(Note: also saved to {output_file})")
        
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
