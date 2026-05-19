"""Analyze archive/iter_218/results/champion_vc_glider.gif to establish ground truth."""
from PIL import Image
from collections import Counter
import os

GIF_PATH = os.path.join("archive", "iter_218", "results", "champion_vc_glider.gif")


def main():
    img = Image.open(GIF_PATH)
    width, height = img.size

    # Count frames
    frame_count = 0
    try:
        while True:
            img.seek(frame_count)
            frame_count += 1
    except EOFError:
        pass

    print(f"GIF path: {GIF_PATH}")
    print(f"Dimensions: {width} x {height}")
    print(f"Total frames: {frame_count}")
    print(f"Mode: {img.mode}")

    # Determine background color from first frame
    img.seek(0)
    f0 = img.convert("RGB")
    pixels0 = list(f0.getdata())
    counter0 = Counter(pixels0)
    background = counter0.most_common(1)[0][0]
    bg_count = counter0.most_common(1)[0][1]
    print(f"Background color (most common in frame 0): {background}  count={bg_count}/{width*height}")
    print(f"Top 5 colors frame 0: {counter0.most_common(5)}")

    # Iterate frames, count non-bg pixels, collect centroid stats
    requested = [0, 50, 100, 150, frame_count - 1]
    report_frames = sorted({f for f in requested if 0 <= f < frame_count})

    per_frame = []
    for i in range(frame_count):
        img.seek(i)
        f = img.convert("RGB")
        px = f.load()
        non_bg = 0
        sum_x, sum_y = 0, 0
        min_x, min_y, max_x, max_y = width, height, -1, -1
        for y in range(height):
            for x in range(width):
                if px[x, y] != background:
                    non_bg += 1
                    sum_x += x
                    sum_y += y
                    if x < min_x: min_x = x
                    if y < min_y: min_y = y
                    if x > max_x: max_x = x
                    if y > max_y: max_y = y
        if non_bg > 0:
            cx = sum_x / non_bg
            cy = sum_y / non_bg
            bbox = (min_x, min_y, max_x, max_y)
        else:
            cx, cy = float("nan"), float("nan")
            bbox = None
        per_frame.append((i, non_bg, cx, cy, bbox))

    print("\n--- Reported frames ---")
    print(f"{'frame':>6} {'non_bg':>8} {'cx':>8} {'cy':>8}  bbox")
    for i in report_frames:
        _, n, cx, cy, bbox = per_frame[i]
        print(f"{i:>6} {n:>8} {cx:>8.2f} {cy:>8.2f}  {bbox}")

    # Motion analysis: full per-frame summary every ~ frame_count/20
    step = max(1, frame_count // 20)
    print(f"\n--- Sampled trajectory (every {step} frames) ---")
    print(f"{'frame':>6} {'non_bg':>8} {'cx':>8} {'cy':>8}")
    for i in range(0, frame_count, step):
        _, n, cx, cy, _ = per_frame[i]
        print(f"{i:>6} {n:>8} {cx:>8.2f} {cy:>8.2f}")

    # Stats
    counts = [n for _, n, _, _, _ in per_frame]
    print(f"\nNon-bg pixel count stats: min={min(counts)} max={max(counts)} mean={sum(counts)/len(counts):.2f}")

    # Direction
    if per_frame[0][1] > 0 and per_frame[-1][1] > 0:
        dx = per_frame[-1][2] - per_frame[0][2]
        dy = per_frame[-1][3] - per_frame[0][3]
        print(f"Net centroid displacement (frame 0 -> last): dx={dx:+.2f}, dy={dy:+.2f}")

    # Bit-depth check: look at how many distinct non-bg colors appear across all frames
    all_non_bg_colors = set()
    for i in range(frame_count):
        img.seek(i)
        f = img.convert("RGB")
        for c in f.getdata():
            if c != background:
                all_non_bg_colors.add(c)
    print(f"\nDistinct non-bg colors across all frames: {len(all_non_bg_colors)}")
    if len(all_non_bg_colors) <= 32:
        print(f"Colors: {sorted(all_non_bg_colors)}")


if __name__ == "__main__":
    main()
