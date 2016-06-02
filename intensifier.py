#!/usr/bin/env python3
"""
usage: intensifier.py [-h] [-s {1..99}] [-f {2..20}] [-t TEXT] filename

Intensify an image

positional arguments:
  filename              file to be intensified

optional arguments:
  -h, --help            show this help message and exit
  -s {1..99}, --shake {1..99}
                        maximum amount of shakiness specified as a percentage
                        of the file's shortest axis (default: 10)
  -f {2..20}, --frames {2..20}
                        number of frames in animation (default: 6)
  -t TEXT, --text TEXT  optional text at the bottom
"""

import argparse
import random
import os
from os.path import basename, splitext
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import tempfile
import requests
import subprocess


# ===== DEFAULT OPTIONS =====
REDUCE_PERCENT = 10
FRAMES = 6


def Main(filename, reduce_percent, frames, text):
    """ main function """
    dimensions = GetDimensions(filename)
    cut_pixels = int(min(dimensions) * reduce_percent / 100 / 2)
    Animate(filename, dimensions, cut_pixels, frames, text)


def GetDimensions(filename):
    """ gets the dimensions of `filename` """
    with Image(filename=filename) as img:
        dimensions = (img.width, img.height)
    return(dimensions)


def Animate(filename, dimensions, cut_pixels, frames, text):
    """ creates frames, offsets them, and optionally adds captions """
    new_dimensions = tuple(i-(cut_pixels*2) for i in dimensions)
    coords = GenerateOffsets(frames, cut_pixels)

    with Image() as new_image:
        for coord in (coords[:-1]):
            with Image(filename=filename) as img:
                img.crop(cut_pixels + coord[0], cut_pixels + coord[1],
                         width=new_dimensions[0], height=new_dimensions[1])
                img.format = 'gif'
                with img.sequence[0] as frame:
                    frame.delay = 2

                if text is not None:
                    AddText(img, new_dimensions, text)

                new_image.sequence.append(img.sequence[0])
        new_name = '{:s}-intense.gif'.format(splitext(basename(filename))[0])
        new_image.save(filename=new_name)

    FixDisposal(new_name)


def GenerateOffsets(frames, cut_pixels):
    """ generate random offsets for frames """
    def GenRandom(max_rand):
        return random.randint(-max_rand, max_rand)

    max_rand = int(cut_pixels / 2)
    if frames == 2:
        return([(0, 0), (max_rand, max_rand), (0, 0)])

    finished = False
    while not finished:
        coords = [(0, 0)]
        for i in range(frames):
            good_random = False
            while not good_random:
                new_coord = []
                for point in coords[i]:
                    change = GenRandom(max_rand)
                    while(abs(point + change) > cut_pixels):
                        change = GenRandom(max_rand)
                    new_coord.append(point + change)
                coord_tuple = tuple(new_coord)
                if coord_tuple not in coords[-2:]:
                    coords.append(coord_tuple)
                    good_random = True
        if ((len(coords) == frames + 1) and (coords[-1] == (0, 0))):
            finished = True
    return(coords)


def AddText(img, new_dimensions, text):
    """ adds text to frame """
    font_file = DownloadFont()
    with Drawing() as draw:
        font_size = new_dimensions[1] * .045
        xpos = round(new_dimensions[0] / 2)
        ypos = round(new_dimensions[1] - 1.5 * font_size)
        outline = font_size / 10
        draw.font = font_file
        draw.font_size = font_size
        draw.text_alignment = 'center'
        draw.text_antialias = True
        invis = draw.stroke_color
        draw.stroke_color = Color('#000000')
        draw.fill_color = Color('#ffff00')
        draw.stroke_width = outline
        draw.text(xpos, ypos, text)
        draw.stroke_color = invis
        draw.text(xpos, ypos, text)
        draw(img)
    os.remove(font_file)


def DownloadFont():
    """ downlaods font file """
    font_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ttf')
    url = ("https://github.com/google/fonts/blob/"
           "4a99a0649614f7e582ec184fea5cdeec51702d79/ofl/sourcecodepro/"
           "SourceCodePro-Regular.ttf?raw=true")
    r = requests.get(url)
    if r.status_code == 200:
        with open(font_file.name, "wb") as font:
            font.write(r.content)
    return(font_file.name)


def FixDisposal(new_name):
    convert_return = subprocess.call(["convert", "-dispose", "previous", new_name, new_name])
    return convert_return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intensify an image")
    parser.add_argument('filename', help="file to be intensified")
    parser.add_argument('-s', '--shake', type=int, default=REDUCE_PERCENT,
                        choices=range(1, 100), metavar="{1..99}",
                        help=("maximum amount of shakiness specified as a "
                              "percentage of the file's shortest axis "
                              "(default: %(default)s)"), dest="reduce_percent")
    parser.add_argument('-f', '--frames', type=int, default=FRAMES,
                        choices=range(2, 21), metavar="{2..20}",
                        help=("number of frames in animation "
                              "(default: %(default)s)"))
    parser.add_argument('-t', '--text', help="optional text at the bottom")

    args = parser.parse_args()
    Main(**vars(args))
