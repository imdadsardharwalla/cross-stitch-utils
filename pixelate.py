#!/usr/bin/python3

import argparse
import numpy as np
import os
import sys

import common.stringify as stringify
import common.argtypes as argtypes

from PIL import Image

schemes = [ 'centre', 'mean' ]

def clamp (value, smallest, largest):
    return max (smallest, min (value, largest))

def type_scheme (value):
    scheme = value.lower ().strip ()
    if scheme not in schemes:
        raise argparse.ArgumentTypeError (
            '\'{0}\' must be one of {1}.'.format (
                value, stringify.list (schemes, 'or')))
    return scheme

def get_output_pixel (x, y):
    if args.scheme == 'centre':
        tile_centre_left = tile_size * (x + 0.5)
        tile_centre_top  = tile_size * (y + 0.5)

        tile_centre_left = clamp (int (round (tile_centre_left)), 0, input_image.width  - 1)
        tile_centre_top  = clamp (int (round (tile_centre_top)),  0, input_image.height - 1)

        return input_pixels[tile_centre_left, tile_centre_top]
    elif args.scheme == 'mean':
        tile_left   = tile_size * x
        tile_top    = tile_size * y
        tile_right  = tile_size * (x + 1)
        tile_bottom = tile_size * (y + 1)

        tile_left   = clamp (int (round (tile_left)),    0, input_image.width  - 1)
        tile_top    = clamp (int (round (tile_top)),     0, input_image.height - 1)
        tile_right  = clamp (int (round (tile_right)),   0, input_image.width  - 1)
        tile_bottom = clamp (int (round (tile_bottom)),  0, input_image.height - 1)

        mean = np.array ([0, 0, 0])
        for i in range (tile_top, tile_bottom):
            for j in range (tile_left, tile_right):
                mean += np.array (input_pixels[j, i])

        for c in range (3):
            mean[c] = int (round (mean[c] / (tile_size * tile_size)))
            mean[c] = clamp (mean[c], 0, 255)

        return tuple (mean)

    return 0


parser = argparse.ArgumentParser ('Creates a one-pixel-per-cross-stitch representation of your image', add_help=False)

parser.add_argument('--help', action='help', help='Show this help message and exit')

dimensions_group = parser.add_mutually_exclusive_group (required=True)
dimensions_group.add_argument ('-w', '--width', type=argtypes.non_negative_int,
                               help='Number of cross stitches along width of image. Cannot be used with -h.')
dimensions_group.add_argument ('-h', '--height', type=argtypes.non_negative_int,
                               help='Number of cross stitches along height of image. Cannot be used with -w.')

parser.add_argument ('-s', '--scheme', type=type_scheme, default=schemes[0],
                     help='Scheme for pixelation. Set to {0}. Default = \'{1}\'.'.format (
                         stringify.list (schemes, 'or'),
                         schemes[0]))

parser.add_argument ('input_image', type=str,
                     help='Path to input image')
parser.add_argument ('output_image', type=str, default='pixelate_out.png',
                     help='Path to store pixelated image')

args = parser.parse_args ()

if not os.path.isfile (args.input_image):
    raise Exception ('input image does not exist.')

with Image.open (args.input_image) as input_image:
    output_width  = 0
    output_height = 0
    tile_size     = 0
    if args.width is None:
        output_height = args.height
        output_width  = int (round (float (input_image.width) / input_image.height * output_height))
        tile_size     = float (input_image.height) / output_height
    else:
        output_width  = args.width
        output_height = int (round (float (input_image.height) / input_image.width * output_width))
        tile_size     = float (input_image.width) / output_width

    output_image = Image.new ('RGB', (output_width, output_height), 'white')

    input_pixels  = input_image.load ()
    output_pixels = output_image.load ()

    for i in range (output_height):
        for j in range (output_width):
            output_pixels[j, i] = get_output_pixel (j, i)

    output_image.save (args.output_image)
