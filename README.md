# elevpasta
A small python script for applying elevation/"hypsometric" coloring to greyscale heightmaps

Requires numpy and pillow

Designed to allow for layering multiple color scales over different areas. Script is commented to give some direction, but in short, each layer requires:

- A list of elevation steps in increasing order
- A list of RGB colors to color the corresponding steps; for simple stepped coloring, there should be one more colors than steps, with colors covering the intervals between steps (and outside the first and last step); for gradient coloring, there should be as many colors as steps, with each color corresponding to each elevation and then colors in between interpolated between elevations.
- A dictionary defining various settings and referencing the above, to be added to the layers list.

The script takes in one (or potentially multiple overlaid) greyscale heightmap image and outputs a colored .png
