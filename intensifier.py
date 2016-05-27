#!/usr/bin/env python3
import random
import os
from os.path import basename,splitext
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from wand.font import Font
import tempfile
import requests
import argparse


def GetDimensions(filename):
  with Image(filename=filename) as img:
    dimensions = (img.width, img.height)
  return(dimensions)


def GenerateOffsets(frames, cutPixels):
  maxRand = int(cutPixels / 2)
  if frames == 2:
    return([(0,0),(maxRand, maxRand), (0,0)])

  finished = False

  while not finished:
    coords = [(0,0)]
    for i in range(frames):
      goodRandom = False

      while not goodRandom:
        new_coord = []
        for point in coords[i]:
          change=random.randint(-maxRand,maxRand)

          while(abs(point + change) > cutPixels):
            change=random.randint(-maxRand,maxRand)

          new_coord.append(point + change)

        coord_tuple = tuple(new_coord)
        if coord_tuple not in coords[-2:]:
          coords.append(coord_tuple)
          goodRandom = True

    if ((len(coords) == frames+1) and (coords[-1] == (0,0))):
      finished=True

  return(coords)


def DownloadFont():
  fontfile = tempfile.NamedTemporaryFile(delete=False, suffix='.ttf')

  url=("https://github.com/google/fonts/blob/"
       "4a99a0649614f7e582ec184fea5cdeec51702d79/ofl/sourcecodepro/"
       "SourceCodePro-Regular.ttf?raw=true")
  r = requests.get(url)
  if r.status_code == 200:
    with open(fontfile.name, "wb") as font:
      font.write(r.content)

  return(fontfile.name)


def GenerateFrames(filename, cutPixels, frames, dimensions, subtitle):
  newDimensions = tuple(i-(cutPixels*2) for i in dimensions)

  coords = GenerateOffsets(frames, cutPixels)

  with Image() as new_image:
    for coord in (coords[:-1]):
      with Image(filename=filename) as img:
        img.crop(cutPixels+coord[0], cutPixels+coord[1], width=newDimensions[0], height=newDimensions[1])
        img.format = 'gif'
        with img.sequence[0] as frame:
          frame.delay=2

        if subtitle is not None:
          fontFile = DownloadFont()

          with Drawing() as draw:
            fontSize=newDimensions[1]*.045
            xpos=round(newDimensions[0]/2)
            ypos=round(newDimensions[1]-1.5*fontSize)
            outline=fontSize/10
            draw.font = fontFile
            draw.font_size = fontSize
            draw.text_alignment = 'center'
            draw.text_antialias = True
            invis = draw.stroke_color
            with Color('#000000') as black:
              draw.stroke_color = black
            with Color('#ffff00') as yellow:
              draw.fill_color = yellow
            draw.stroke_width = outline
            draw.text(xpos,ypos,subtitle)
            draw.stroke_color=invis
            draw.text(xpos,ypos,subtitle)
            draw(img)
          os.remove(fontFile)

        new_image.sequence.append(img.sequence[0])

    shortname = splitext(basename(filename))[0]
    new_image.save(filename='{:s}-intense.gif'.format(shortname))


def Shake(filename, reducePercent=2, frames=6, delay=2, subtitle=None):
  dimensions = GetDimensions(filename)
  cutPixels = int(min(dimensions) * reducePercent / 100 / 2)
  # print("Cutting {0:d} pixels off all sides ({1:.2%})".format(cutPixels,2*cutPixels/min(dimensions)))
  # newDimensions = tuple(i-10 for i in dimensions)
  # print('Reducing image size by {1:02d}% (final dimensions: {0})'.format(newDimensions,reducePercent))

  GenerateFrames(filename, cutPixels, frames, dimensions, subtitle)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Intensify an image")
  parser.add_argument('filename', help="file to be intensified")
  parser.add_argument('-s', '--shake', type=int, default=10, choices=range(1,100), metavar="{1..99}", help="maximum amount of shakiness specified as a percentage of the file's shortest axis (default: %(default)s)")
  parser.add_argument('-f', '--frames', type=int, default=6, choices=range(2,21), metavar="{2..20}", help="number of frames in animation (default: %(default)s)")
  parser.add_argument('-t', '--text', help="optional text at the bottom")
  args=parser.parse_args()

  Shake(filename=args.filename, reducePercent=args.shake, frames=args.frames, subtitle=args.text)
