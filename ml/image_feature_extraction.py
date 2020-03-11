#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob

import numpy as np
from PIL import Image, ImageFile
from skimage.measure import shannon_entropy

import common

FEATURE = "image"
ImageFile.LOAD_TRUNCATED_IMAGES = True


def load_images_as_greyscale(files):
    """
        Beware: Takes a lot of memory (on avg., 2400 images from TWPC == 2.5 GB, ~16 GB memory.)
    """
    print(f"Loading images in {files}")
    files = glob.glob(files + "/*")
    global images
    images = [Image.open(im).convert("L") for im in files]


def clear():
    global images
    images.clear()


def image_sharpness(sp, df):
    print(f"Computing sharpness on {len(df)} images")

    def compute(im):
        # i2 = Image.open(im).convert("L")
        array = np.asarray(im, dtype=np.int32)
        gy, gx = np.gradient(array)
        gnorm = np.sqrt(gx ** 2 + gy ** 2)
        sharpness = np.average(gnorm)
        # sys.stdout.write("\r" + f"{n}")
        return sharpness

    results = common.for_dataframe(images, df, "sharpness", FEATURE, compute)
    print()
    common.save_scores(results, sp=sp, db=False)
    print("_" * 100)


def image_shannon_entropy(sp, df):
    print(f"Computing shannon entropy on {len(df)} images")

    def compute(im):
        # im = Image.open(im).convert("L")
        array = np.asarray(im, dtype=np.int32)
        entropy = shannon_entropy(array)
        # sys.stdout.write("\r" + f"{n}")
        return entropy

    results = common.for_dataframe(images, df, "shannon", FEATURE, compute)
    print()
    common.save_scores(results, sp=sp, db=False)
    print("_" * 100)


images = []
