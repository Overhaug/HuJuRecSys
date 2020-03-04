#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Simple definitions module to automatically setup paths on windows and mac.
"""

import os
import platform


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFINITIONS = "/definitions.txt"


def setup_paths():
    """
        Run this function once from root to setup definitions.
        cd into root, and do: import definitions, followed by definitions.setup_paths()
        Creates a file "definitions.txt" in the root folder.
    """
    current_os = platform.system()
    datadir = "data/"
    corpusdir = datadir + "corpus/"
    imagedir = "images/sorted/"
    sep = ";"

    if current_os == "Darwin":
        basedir = "/Volumes/Samsung_T5/"
        datadir = basedir + datadir
        imagedir = basedir + imagedir
        corpusdir = basedir + corpusdir
    elif current_os == "Windows":
        basedir = "E:/"
        datadir = basedir + datadir
        imagedir = basedir + imagedir
        corpusdir = basedir + corpusdir
    else:
        raise OSError("Linux not supported.")

    with open(ROOT_DIR + DEFINITIONS, "w") as w:
        b = "basedir" + sep + basedir
        d = "datadir" + sep + datadir
        i = "imagedir" + sep + imagedir
        c = "corpusdir" + sep + corpusdir
        entity = b + "\n" + d + "\n" + i + "\n" + c
        w.write(entity)
        w.close()


def get_paths():
    """
        Gets paths from definitions.txt, and creates a dictionary of these.
    :return: A dictionary containing paths.
    """
    with open(ROOT_DIR + DEFINITIONS, "r") as r:
        paths = r.readlines()
        return {line.split(";")[0].strip(): line.split(";")[1].strip() for line in paths}
