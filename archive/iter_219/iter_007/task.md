All attempts to reproduce the v<c glider from iter_218 have failed. The goal of this task is to analyze the original animation from that iteration to establish a ground truth.

**Task: Analyze `archive/iter_218/results/champion_vc_glider.gif`**

Write and execute a Python script using the Pillow library (`PIL`) to inspect the GIF file. The script must:
1.  Open `archive/iter_218/results/champion_vc_glider.gif`.
2.  Count and report the total number of frames in the animation.
3.  Get and report the dimensions (width, height) of the GIF.
4.  Iterate through the frames and, for each frame, count the number of non-background pixels. Assume the background is the most common color in the first frame's palette.
5.  Report the pixel count for frames 0, 50, 100, 150, and the final frame.
6.  Describe the motion of the non-background pixels. Does a coherent object move across the frame?
7.  Summarize the findings. Does the GIF show a 10-bit glider, a 3-bit object, or something else entirely? This is the most important output.