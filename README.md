png-draw-data
=============

**png-draw-data** extracts text appended to the end of PNG files and renders it
into the image itself.

PNG files can contain arbitrary data after the end of the image. For PNG files
that store ASCII or UTF-8 text in this manner, this program can extract
configurable parts of that text and render it into the image itself.

Usage
-----

Run `./png-draw-data.py` for usage information.

png-draw-data is configurable via [config.ini](config.ini) and
[patterns.txt](patterns.txt). patterns.txt contains pairs of lines, separated
by blank lines, where the first line in each pair is a regular expression used
with [Python’s `re` module][re] with the options [`re.VERBOSE`] and
[`re.MULTILINE`], and the second line is a template string used with
[`re.Match.expand()`][expand].

[re]: https://docs.python.org/3/library/re.html
[`re.VERBOSE`]: https://docs.python.org/3/library/re.html#re.VERBOSE
[`re.MULTILINE`]: https://docs.python.org/3/library/re.html#re.MULTILINE
[expand]: https://docs.python.org/3/library/re.html#re.Match.expand

Dependencies
------------

* Python ≥ 3.7
* Python package: [Pillow]

Run `pip3 install -r requirements.txt` to install the Python packages. You can
also use `requirements.freeze.txt` instead to install specific versions of the
dependencies that have been verified to work.

[Pillow]: https://pypi.org/project/Pillow

License
-------

png-draw-data is licensed under version 3 or later of the GNU Affero General
Public License. See [LICENSE](LICENSE).
