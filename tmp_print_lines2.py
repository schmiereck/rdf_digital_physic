with open('src/new_fitness.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
for i in range(290, min(320, len(lines))):
    output_lines.append('{0:4d}: {1}'.format(i + 1, lines[i].rstrip('\n')))

with open('tmp_output2.txt', 'w', encoding='utf-8') as out:
    out.write('\n'.join(output_lines) + '\n')
