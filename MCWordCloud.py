# Author: Andreas Christian Mueller <t3kcit@gmail.com>
#
# (c) 2012
# Modified by: Paul Nechifor <paul@nechifor.net>
# Modified by: Michael Chiang
# License: MIT

import warnings
from random import Random
import os
import re
import sys
import colorsys
import numpy as np
from operator import itemgetter

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont


item1 = itemgetter(1)

FONT_PATH = os.environ.get("FONT_PATH", os.path.join(os.path.dirname(__file__),
                                                     "DroidSansMono.ttf"))



class IntegralOccupancyMap(object):
    def __init__(self, height, width, mask):
        self.height = height
        self.width = width
        if mask is not None:
            # the order of the cumsum's is important for speed ?!
            self.integral = np.cumsum(np.cumsum(255 * mask, axis=1),
                                      axis=0).astype(np.uint32)
        else:
            self.integral = np.zeros((height, width), dtype=np.uint32)

    def sample_position(self, size_x, size_y, random_state):
        return query_integral_image(self.integral, size_x, size_y, random_state)

    def update(self, img_array, pos_x, pos_y):
        partial_integral = np.cumsum(np.cumsum(img_array[pos_x:, pos_y:], axis=1),
                                     axis=0)
        # paste recomputed part into old image
        # if x or y is zero it is a bit annoying
        if pos_x > 0:
            if pos_y > 0:
                partial_integral += (self.integral[pos_x - 1, pos_y:]
                                     - self.integral[pos_x - 1, pos_y - 1])
            else:
                partial_integral += self.integral[pos_x - 1, pos_y:]
        if pos_y > 0:
            partial_integral += self.integral[pos_x:, pos_y - 1][:, np.newaxis]

        self.integral[pos_x:, pos_y:] = partial_integral



def generate_from_frequencies(frequencies):
    # constants
    max_words=200
    height=200
    width=400
    max_font_size=height

    # make sure frequencies are sorted and normalized
    frequencies = sorted(frequencies, key=item1, reverse=True)
    frequencies = frequencies[:max_words]
    # largest entry will be 1
    max_frequency = float(frequencies[0][1])

    frequencies = [ (word, freq / max_frequency) for word, freq in frequencies ]



    random_state = Random()

    if len(frequencies) <= 0:
        print("We need at least 1 word to plot a word cloud, got %d."
              % len(frequencies))


    boolean_mask = None
    height, width = height, width
    occupancy = IntegralOccupancyMap(height, width, boolean_mask)

    # create image
    img_grey = Image.new("L", (width, height))
    draw = ImageDraw.Draw(img_grey)
    img_array = np.asarray(img_grey)
    font_sizes, positions, orientations, colors = [], [], [], []

    font_size = max_font_size
    last_freq = 1.

    # start drawing grey image
    for word, freq in frequencies:
        # select the font size
        rs = self.relative_scaling
        if rs != 0:
            font_size = int(round((rs * (freq / float(last_freq)) + (1 - rs)) * font_size))
        while True:
            # try to find a position
            font = ImageFont.truetype(self.font_path, font_size)
            # transpose font optionally
            if random_state.random() < self.prefer_horizontal:
                orientation = None
            else:
                orientation = Image.ROTATE_90
            transposed_font = ImageFont.TransposedFont(font,
                                                       orientation=orientation)
            # get size of resulting text
            box_size = draw.textsize(word, font=transposed_font)
            # find possible places using integral image:
            result = occupancy.sample_position(box_size[1] + self.margin,
                                               box_size[0] + self.margin,
                                               random_state)
            if result is not None or font_size == 0:
                break
            # if we didn't find a place, make font smaller
            font_size -= self.font_step

        if font_size < self.min_font_size:
            # we were unable to draw any more
            break

        x, y = np.array(result) + self.margin // 2
        # actually draw the text
        draw.text((y, x), word, fill="white", font=transposed_font)
        positions.append((x, y))
        orientations.append(orientation)
        font_sizes.append(font_size)
        colors.append(self.color_func(word, font_size=font_size,
                                      position=(x, y),
                                      orientation=orientation,
                                      random_state=random_state,
                                      font_path=self.font_path))
        # recompute integral image
        if self.mask is None:
            img_array = np.asarray(img_grey)
        else:
            img_array = np.asarray(img_grey) + boolean_mask
        # recompute bottom right
        # the order of the cumsum's is important for speed ?!
        occupancy.update(img_array, x, y)
        last_freq = freq

    self.layout_ = list(zip(frequencies, font_sizes, positions, orientations, colors))
    return self
