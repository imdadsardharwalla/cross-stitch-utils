#!/usr/bin/python3

import argparse
import math
import numpy as np
import os
import sys

np.set_printoptions(threshold=sys.maxsize)

from sklearn.cluster import KMeans

import common.stringify    as stringify
import common.argtypes     as argtypes
import common.colourspaces as colourspaces

from PIL import Image

# Boost Y co-ordinate to ensure that a change in luma is more
# important than a change in chroma
Y_boost = 1.5

parser = argparse.ArgumentParser ('TODO', add_help=False)

parser.add_argument('--help', action='help', help='Show this help message and exit')

parser.add_argument ('-c', '--max-colours', type=argtypes.non_negative_int,
                     help='Maximum number of colours used TODO')

parser.add_argument ('-t', '--threshold', type=float, required=True,
                     help='TODO')

parser.add_argument ('input_image', type=str,
                     help='Path to input image')
# TODO
parser.add_argument ('output_image', type=str, default='pixelate_out.png',
                     help='Path to store pixelated image')

args = parser.parse_args ()

if not os.path.isfile (args.input_image):
    raise Exception ('input image does not exist.')

with Image.open (args.input_image) as input_image:
    input_pixels = input_image.load ()
    input_colours = np.zeros ([input_image.width * input_image.height, 3])

    # convert "tuple" pixel map provided by the Pillow library to a
    # numpy array
    for i in range (input_image.height):
        for j in range (input_image.width):
            input_colours[i * input_image.width + j] = \
                colourspaces.RGB_to_YPbPr (np.array (input_pixels[j, i]), Y_boost)

    colours_ub = args.max_colours
    colours_lb = 0
    colours_current = args.max_colours

    clusters_ub = None

    while colours_ub - colours_lb > 1:

        print ("k means clustering with max colours={0}".format (colours_current))
        clusters = KMeans (n_clusters=colours_current)
        centroid_distances = clusters.fit_transform (input_colours)

        cluster_dist = np.zeros (input_image.width * input_image.height)
        within_threshold = True
        for i in range (input_image.height * input_image.width):
            distance = centroid_distances[i, clusters.labels_[i]]
            cluster_dist[i] = distance
            if distance > args.threshold:
                within_threshold = False
                break

        if within_threshold:
            # too many colours
            colours_ub = colours_current
            clusters_ub = clusters
        else:
            # too few colours
            colours_lb = colours_current

        colours_current = int (round ((colours_lb + colours_ub) * 0.5))

    required_colours = len (clusters.cluster_centers_)#colours_ub
    print ("Required colours = {0}".format (required_colours))

    output_image = Image.new ('RGB', (input_image.width, input_image.height), 'white')
    output_pixels = output_image.load ()

    output_colours = [clusters_ub.cluster_centers_[x] for x in clusters_ub.predict (input_colours)]
    for i in range (input_image.height):
        for j in range (input_image.width):
            current_pixel = colourspaces.YPbPr_to_RGB (output_colours[i * input_image.width + j], Y_boost)
            current_pixel_i = [0, 0, 0]
            for c in range (3):
                current_pixel_i[c] = int (round (current_pixel[c]))
            output_pixels[j, i] = tuple (current_pixel_i)

    output_image.save (args.output_image)
