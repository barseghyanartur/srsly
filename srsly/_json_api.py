# coding: utf8
from __future__ import unicode_literals

import sys
from pathlib import Path

from .json import ujson


def read_json(location):
    """Load JSON from file or standard input.

    location (unicode / Path): The file path. "-" for reading from stdin.
    RETURNS (dict / list): The loaded JSON content.
    """
    if location == "-":  # reading from sys.stdin
        data = sys.stdin.read()
        return ujson.loads(data)
    file_path = _force_path(location)
    with file_path.open("r", encoding="utf8") as f:
        return ujson.load(f)


def write_json(location, data, indent=2):
    """Create a .json file and dump contents or write to standard
    output.

    location (unicode / Path): The file path. "-" for writing to stdout.
    data: The JSON-serializable data to output.
    indent (int): Number of spaces used to indent JSON.
    """
    json_data = _json_dumps(data, indent=indent)
    if location == "-":  # writing to stdout
        print(json_data)
    else:
        file_path = _force_path(location)
        with file_path.open("w", encoding="utf8") as f:
            f.write(json_data)


def read_jsonl(location, skip=False):
    """Read a .jsonl file or standard input and yield contents line by line.
    Blank lines will always be skipped.

    location (unicode / Path): The file path. "-" for reading from stdin.
    skip (bool): Skip broken lines and don't raise ValueError.
    YIELDS: The loaded JSON contents of each line.
    """
    if location == "-":  # reading from sys.stdin
        for line in _yield_json_lines(sys.stdin, skip=skip):
            yield line
    else:
        file_path = _force_path(location)
        with file_path.open("r", encoding="utf8") as f:
            for line in _yield_json_lines(f, skip=skip):
                yield line


def write_jsonl(location, lines):
    """Create a .jsonl file and dump contents or write to standard output.

    location (unicode / Path): The file path. "-" for writing to stdout.
    lines (list): The JSON-serializable contents of each line.
    """
    if location == "-":  # writing to stdout
        for line in lines:
            print(_json_dumps(line))
    else:
        file_path = _force_path(location)
        with file_path.open("a", encoding="utf-8") as f:
            for line in lines:
                f.write(_json_dumps(line) + "\n")


def is_json_serializable(obj):
    """Check if a Python object is JSON-serializable.

    obj: The object to check.
    RETURNS (bool): Whether the object is JSON-serializable.
    """
    if hasattr(obj, "__call__"):
        # Check this separately here to prevent infinite recursions
        return False
    try:
        ujson.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


def _yield_json_lines(stream, skip=False):
    line_no = 1
    for line in stream:
        line = line.strip()
        if line == "":
            continue
        try:
            yield ujson.loads(line)
        except ValueError:
            if skip:
                continue
            raise ValueError("Invalid JSON on line {}: {}".format(line_no, line))
        line_no += 1


def _force_path(location):
    file_path = Path(location)
    if not file_path.exists():
        raise ValueError("Can't read file: {}".format(location))
    return file_path


def _json_dumps(data, indent=0):
    result = ujson.dumps(data, indent=indent, escape_forward_slashes=False)
    if sys.version_info[0] == 2:  # Python 2
        return result.decode("utf8")
    return result
