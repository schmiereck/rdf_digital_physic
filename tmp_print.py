with open('src/new_fitness.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 130-180
output = []
output.append("=" * 80)
output.append("LINES 130-180:")
output.append("=" * 80)
for i in range(129, min(180, len(lines))):
    output.append('{0:4d}: {1}'.format(i + 1, lines[i].rstrip('\n')))

# The window_steps division section (around line 297-315)
output.append("")
output.append("=" * 80)
output.append("WINDOW_STEPS DIVISION SECTION (lines ~290-320):")
output.append("=" * 80)
for i in range(289, min(320, len(lines))):
    output.append('{0:4d}: {1}'.format(i + 1, lines[i].rstrip('\n')))

with open('tmp_output.txt', 'w', encoding='utf-8') as out:
    out.write('\n'.join(output) + '\n')
