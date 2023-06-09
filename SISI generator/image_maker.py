from PIL import Image
import numpy as np
import jsonpickle
import os

in_labels_file = 'out_labels.json'
in_glyphs_filename = 'out_normalized_glyphs.json'
out_image_bw_folder = 'out_bw_images'
out_image_color_folder = 'out_color_images'
size = 100

os.mkdir(out_image_bw_folder)
os.mkdir(out_image_color_folder)

def interpolated_glyph(glyph, size):
    pixels_path = [ [ 255 for _ in range(size) ] for _ in range(size) ] # holds the path information
    pixels_time = [ [ 255 for _ in range(size) ] for _ in range(size) ] # holds the timing (speed information)
    pixels_ends = [ [ 255 for _ in range(size) ] for _ in range(size) ] # holds info about the endpoints of strokes

    for stroke in glyph:
        prev_x, prev_y = None, None
        for i in range(0, len(stroke), 2):
            x = int(stroke[i] * size)
            y = int(stroke[i+1] * size)
            time = int(i / len(stroke) * 255)

            # target pixel
            pixels_path[y][x] = 0
            pixels_time[y][x] = time

            # interpolation
            if prev_x is not None:
                delta_x = prev_x - x 
                delta_y = prev_y - y

                steps_count = max(abs(delta_x), abs(delta_y))
                for step in range(steps_count):
                        pixels_path[y + int(delta_y * step / steps_count)][x + int(delta_x * step / steps_count)] = 0
                        pixels_time[y + int(delta_y * step / steps_count)][x + int(delta_x * step / steps_count)] = time

            # setup for next iteration
            prev_x = x
            prev_y = y

    for stroke in glyph:
        start_x = int(stroke[0] * size)
        start_y = int(stroke[1] * size)
        end_x = int(stroke[-2] * size)
        end_y = int(stroke[-1] * size)

        pixels_ends[start_y][start_x] = 0
        pixels_ends[end_y][end_x] = 0

    return pixels_path, pixels_time, pixels_ends

with open(in_glyphs_filename, 'r') as glyphs_file, open(in_labels_file, 'r') as labels_file:
    glyphs = jsonpickle.decode(glyphs_file.read())
    labels = jsonpickle.decode(labels_file.read())

    for n, glyph in enumerate(glyphs):
        if n % 1000 == 0:
            print(f'Done {n}')
        
        pixels_path, pixels_time, pixels_end = interpolated_glyph(glyph, size)
        pixels_merged = [ [ (pixels_path[i][j], pixels_time[i][j], pixels_end[i][j] ) for j in range(size) ] for i in range(size) ]

        label = labels[n]
        if label == '?':
            label = 'questionmark'
        elif label == '"':
            label = 'doublequote'
        elif label == '<':
            label = 'leftanglebracket'
        elif label == '>':
            label = 'rightanglebracket'
        elif label == ':':
            label = 'colon'

        color_image = Image.fromarray(np.array(pixels_merged, dtype=np.uint8))
        color_image.save(f'{out_image_color_folder}/{n}-{label}.png')

        bw_image = Image.fromarray(np.array(pixels_path, dtype=np.uint8))
        bw_image.save(f'{out_image_bw_folder}/{n}-{label}.png')
