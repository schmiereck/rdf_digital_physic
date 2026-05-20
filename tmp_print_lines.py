with open('src/new_fitness.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
for i in range(129, min(180, len(lines))):
    output_lines.append('{0:4d}: {1}'.format(i + 1, lines[i].rstrip('\n')))

with open('tmp_output.txt', 'w', encoding='utf-8') as out:
    out.write('\n'.join(output_lines) + '\n')
