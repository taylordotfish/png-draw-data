#!/usr/bin/env python3
# Copyright (C) 2021 taylor.fish <contact@taylor.fish>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from configparser import ConfigParser, DEFAULTSECT
from dataclasses import dataclass
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import List
import os
import os.path
import re
import sys

USAGE = f"""\
Usage: {sys.argv[0]} <input> <output>

If <input> is a PNG file, <output> should be the name of the new PNG file that
will be created.

If <input> is a folder, all PNG files in that folder (but not subfolders) will
be processed. <output> should be the name of the folder where the new PNG files
will be saved. (It will be created if it doesn't already exist.)
"""

# Whether to refuse to run if the input and output are the same.
PREVENT_INPUT_OVERWRITE = True
SCRIPT_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.ini")
PATTERNS_PATH = os.path.join(SCRIPT_DIR, "patterns.txt")
DEFAULT_TTF = os.path.join(SCRIPT_DIR, "noto/NotoSansMono-Regular.ttf")
PNG_END = b"IEND\xAE\x42\x60\x82"
BATCH_SUFFIX: str = None
PATTERNS: List["Pattern"] = None
FONT: ImageFont.ImageFont = None


@dataclass
class Pattern:
    regex: re.Pattern
    template: str


def get_patterns() -> List[Pattern]:
    def generate():
        with open(PATTERNS_PATH, encoding="utf8") as f:
            for chunk in f.read().split("\n\n"):
                regex, template = chunk.splitlines()
                yield Pattern(
                    regex=re.compile(regex, re.MULTILINE | re.VERBOSE),
                    template=template,
                )
    return list(generate())


def get_formatted_text(path: str, trailing: str) -> str:
    def get_parts():
        for pattern in PATTERNS:
            match = pattern.regex.search(trailing)
            if match is not None:
                yield match.expand(pattern.template)
                continue
            print(
                f"warning: did not find [{pattern.regex.pattern}] in {path}",
                file=sys.stderr
            )
    return "\n".join(get_parts())


def draw_text(text: str, width: int) -> Image.Image:
    draw = ImageDraw.Draw(Image.new("RGB", (0, 0)))
    _, height = draw.multiline_textsize(text, font=FONT)
    image = Image.new("RGB", (width, height + FONT.size // 2), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.multiline_text((FONT.size // 4, 0), text, fill=(0, 0, 0), font=FONT)
    return image


def process_file(in_path: str, out_path: str):
    with open(in_path, "rb") as f:
        data = f.read()

    try:
        end_index = data.rindex(PNG_END)
    except ValueError:
        print(
            f"warning: couldn't find end of PNG data in {in_path}",
            file=sys.stderr,
        )
        return

    end_index += len(PNG_END)
    trailing = data[end_index:]
    trailing_str = trailing.decode("utf8", errors="replace")
    data = data[:end_index]
    text = get_formatted_text(in_path, trailing_str)

    image = Image.open(BytesIO(data))
    text = draw_text(text, image.width)
    new_image = Image.new("RGB", (image.width, image.height + text.height))
    new_image.paste(image, (0, 0))
    new_image.paste(text, (0, image.height))
    new_image.save(out_path, "PNG")
    with open(out_path, "ab") as f:
        f.write(trailing)


def process_dir(in_path: str, out_path: str):
    try:
        os.mkdir(out_path)
    except FileExistsError:
        if not os.path.isdir(out_path):
            print(f"error: not a folder: {out_path}", file=sys.stderr)
            sys.exit(1)
    for entry in os.scandir(in_path):
        name, ext = os.path.splitext(entry.name)
        if entry.is_file() and ext.lower() == ".png":
            process_file(
                entry.path,
                os.path.join(out_path, name + BATCH_SUFFIX + ext),
            )


def process(in_path: str, out_path: str):
    if os.path.isdir(in_path):
        process_dir(in_path, out_path)
    else:
        process_file(in_path, out_path)


def samefile(path1: str, path2: str) -> bool:
    try:
        return os.path.samefile(path1, path2)
    except FileNotFoundError:
        return False


def main():
    global BATCH_SUFFIX
    global PATTERNS
    global FONT

    if len(sys.argv) != 3:
        print(USAGE, end="", file=sys.stderr)
        sys.exit(1)

    config = ConfigParser()
    with open(CONFIG_PATH, encoding="utf8") as f:
        config.read_string(f"[{DEFAULTSECT}]\n{f.read()}")
    config = config[DEFAULTSECT]

    BATCH_SUFFIX = config["batch-suffix"]
    PATTERNS = get_patterns()
    FONT = ImageFont.truetype(
        config["font-file"] or DEFAULT_TTF,
        size=int(config["font-size"]),
    )

    in_path, out_path = sys.argv[1:]
    if PREVENT_INPUT_OVERWRITE and samefile(in_path, out_path):
        print("error: input and output paths are the same", file=sys.stderr)
        sys.exit(1)
    process(in_path, out_path)


if __name__ == "__main__":
    main()
