#!/usr/bin/python3

import argparse
import math
import numpy as np
import os
import sys

np.set_printoptions(threshold=sys.maxsize)

import common.stringify    as stringify
import common.argtypes     as argtypes
import common.colourspaces as colourspaces

from PIL import Image

parser = argparse.ArgumentParser ('TODO', add_help=False)

parser.add_argument('--help', action='help', help='Show this help message and exit')

parser.add_argument ('input_image', type=str,
                     help='Path to input image')
parser.add_argument ('output_image', type=str, default='',
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


    colour_palette = Image.new ('RGB', (1, num_unique_colours), 'white')
    colour_palette_pixels = colour_palette.load ()

    for i in range (num_unique_colours):
        current_pixel = input_colours_rgb_hsl[i]
        current_pixel_i = [0, 0, 0]
        for c in range (3):
            current_pixel_i[c] = int (round (current_pixel[c]))

        colour_palette_pixels[0, i] = tuple (current_pixel_i)

    colour_palette.save ("./palette.png")
