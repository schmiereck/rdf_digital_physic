"""Extract sample frames and run a finer-grained diff analysis."""
from PIL import Image, ImageChops
import os

GIF_PATH = os.path.join("archive", "iter_218", "results", "champion_vc_glider.gif")
OUT_DIR = os.path.join("archive", "iter_219", "iter_007", "frames")
os.makedirs(OUT_DIR, exist_ok=True)

img = Image.open(GIF_PATH)
width, height = img.size

frames = []
i = 0
try:
    while True:
        img.seek(i)
        frames.append(img.convert("RGB").copy())
        i += 1
except EOFError:
    pass

print(f"Loaded {len(frames)} frames")

# Save a few frames
for idx in [0, 10, 20, 30, 40]:
    if idx < len(frames):
        frames[idx].save(os.path.join(OUT_DIR, f"frame_{idx:03d}.png"))
        print(f"Saved frame_{idx:03d}.png")

# Diff analysis: count pixels that changed between consecutive frames
print("\n--- Inter-frame diffs ---")
print(f"{'i->i+1':>8} {'changed_px':>12} {'bbox_of_change'}")
for i in range(len(frames) - 1):
    diff = ImageChops.difference(frames[i], frames[i + 1])
    bbox = diff.getbbox()
    # Count changed pixels
    pixels = diff.load()
    changed = 0
    for y in range(height):
        for x in range(width):
            if pixels[x, y] != (0, 0, 0):
                changed += 1
    print(f"{i:>3}->{i+1:>3} {changed:>12}  {bbox}")

# Diff between frame 0 and final frame
diff = ImageChops.difference(frames[0], frames[-1])
bbox = diff.getbbox()
pixels = diff.load()
changed = 0
for y in range(height):
    for x in range(width):
        if pixels[x, y] != (0, 0, 0):
            changed += 1
print(f"\nFrame 0 vs frame {len(frames)-1}: changed={changed}  bbox={bbox}")
