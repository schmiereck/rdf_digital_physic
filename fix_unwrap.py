import re

with open("src/new_fitness.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """        unwrapped_coms: list[tuple[float, float]] = [sorted_history[0]["com"]]
        for i in range(1, len(sorted_history)):
            prev_com = sorted_history[i - 1]["com"]
            cur_com = sorted_history[i]["com"]
            dx = cur_com[0] - prev_com[0]
            dy = cur_com[1] - prev_com[1]
            # Assume grid wraps at 128 (GRID_SIZE).  Unwrap deltas:
            if dx > 64:
                dx -= 128.0
            elif dx < -64:
                dx += 128.0
            if dy > 64:
                dy -= 128.0
            elif dy < -64:
                dy += 128.0
            unwrapped_coms.append((prev_com[0] + dx, prev_com[1] + dy))"""

replacement = """        unwrapped_coms: list[tuple[float, float]] = [sorted_history[0]["com"]]
        for i in range(1, len(sorted_history)):
            prev_com = sorted_history[i - 1]["com"]
            cur_com = sorted_history[i]["com"]
            dx = cur_com[0] - prev_com[0]
            dy = cur_com[1] - prev_com[1]
            if dx > 64:
                dx -= 128.0
            elif dx < -64:
                dx += 128.0
            if dy > 64:
                dy -= 128.0
            elif dy < -64:
                dy += 128.0
            last_unwrapped = unwrapped_coms[-1]
            unwrapped_coms.append((last_unwrapped[0] + dx, last_unwrapped[1] + dy))"""

if target in content:
    content = content.replace(target, replacement)
    with open("src/new_fitness.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully replaced target block!")
else:
    # Try with slightly different whitespace / comment
    print("Target block not found precisely. Let's check with a simpler replacement.")
    # Fallback/specific replacement:
    old_line = "unwrapped_coms.append((prev_com[0] + dx, prev_com[1] + dy))"
    new_lines = """last_unwrapped = unwrapped_coms[-1]
            unwrapped_coms.append((last_unwrapped[0] + dx, last_unwrapped[1] + dy))"""
    if old_line in content:
        content = content.replace(old_line, new_lines)
        with open("src/new_fitness.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("Successfully replaced old line!")
    else:
        print("Could not find line either!")
