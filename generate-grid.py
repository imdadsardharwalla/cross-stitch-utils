#!/usr/bin/python3

import argparse
import glob
import math
import numpy as np
import os
import random
import sys

np.set_printoptions(threshold=sys.maxsize)

import common.stringify    as stringify
import common.argtypes     as argtypes
import common.colourspaces as colourspaces

from PIL import Image

tile_size = 50

parser = argparse.ArgumentParser ('TODO', add_help=False)

parser.add_argument('--help', action='help', help='Show this help message and exit')

parser.add_argument ('input_image', type=str,
                     help='Path to input image')
parser.add_argument ('output_image', type=str, default='',
                     help='Path to store output grid')
parser.add_argument ('output_palette', type=str, default='',
                     help='Path to store colour palette')

args = parser.parse_args ()

if not os.path.isfile (args.input_image):
    raise Exception ('input image does not exist.')

with Image.open (args.input_image) as input_image:
    input_pixels = input_image.load ()

    input_colours_rgb = set ()
    for i in range (input_image.height):
        for j in range (input_image.width):
            input_colours_rgb.update ([ input_pixels[j, i] ])

    input_colours_rgb_matrix = [ list (x) for x in input_colours_rgb ]
    num_unique_colours = len (input_colours_rgb)
    input_colours_rgb_hsl = []

    for i in range (num_unique_colours):
        rgb = input_colours_rgb_matrix[i]
        hsl = colourspaces.RGB_to_HSL (rgb).tolist ()

        input_colours_rgb_hsl += [ rgb + hsl ]


    input_colours_rgb_hsl.sort (key=colourspaces.HSL_sort)

    colour_palette = [ (R, G, B) for [R, G, B, H, S, L] in input_colours_rgb_hsl ]

    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    symbols_dir = os.path.join (script_dir, "symbols/")
    symbols_files = glob.glob (os.path.join (symbols_dir, "*.png"))

    symbols_original = [ Image.open (x) for x in symbols_files ]

    # shuffle the symbols
    random.seed (8)
    random.shuffle (symbols_original)

    symbols = [ x.resize ((tile_size, tile_size)) for x in symbols_original ]

    border_depth = int (round (tile_size * 0.07))
    grid_width  = input_image.width  * (tile_size + border_depth) - border_depth
    grid_height = input_image.height * (tile_size + border_depth) - border_depth

    output_image = Image.new ('RGBA', (grid_width, grid_height), 'white')

    for i in range (input_image.height):
        for j in range (input_image.width):
            index = colour_palette.index (input_pixels[j, i])
            output_image.paste (symbols[index], \
                                (j * (tile_size + border_depth), i * (tile_size + border_depth)), \
                                symbols[index])

    dark_border  = tuple ((  0,   0,   0, 255))
    light_border = tuple ((192, 192, 192, 255))

    output_pixels = output_image.load ()
    for i in range (1, input_image.height - 1):
        for x in range (grid_width):
            for y in range (border_depth):
                border_colour = dark_border if (i % 10 == 0) else light_border
                output_pixels[x, i * (tile_size + border_depth) - y] = border_colour

    for j in range (1, input_image.width - 1):
        for y in range (grid_height):
            for x in range (border_depth):
                border_colour = dark_border if (j % 10 == 0) else light_border
                current_colour = output_pixels[j * (tile_size + border_depth) - x, y]

                if current_colour != dark_border:
                    output_pixels[j * (tile_size + border_depth) - x, y] = border_colour


    output_image.save (args.output_image)

    colour_palette_image = Image.new ('RGBA', (num_unique_colours * tile_size, tile_size * 2), 'white')

    for j in range (num_unique_colours):
        colour_palette_image.paste (symbols[j], (j * tile_size, 0), symbols[j])

    colour_palette_pixels = colour_palette_image.load ()

    for j in range (num_unique_colours):
        for x in range (tile_size):
            for y in range (tile_size):
                colour_palette_pixels[j * tile_size + x, tile_size + y] = colour_palette[j]

    colour_palette_image.save (args.output_palette)
