# intensifier
Requirements:
* ImageMagick (http://www.imagemagick.org/script/index.php)
* wand (http://docs.wand-py.org/en/0.4.2/)
* requests (http://docs.python-requests.org/en/master/)

```
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
  ```
