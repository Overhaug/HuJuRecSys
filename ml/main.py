#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for running: Initial sampling -> Similarity functions
    -> Processing images -> Combining metrics -> Creating quantiles -> Sampling from quantiles
    in one run
"""

import os

import definitions
import metric_combiner
import preprocess_images
import quantiles
import similarity_functions
import utils
from sampler import sample_n_per_year


def init_new_category_mainfile(category):
    d = utils.get_df(source="E:/data/twp_corpus_politics.csv",
                     category=category, dt=True, drop_duplicates=True, drop_nans=True,
                     has_image=True, drop_missing_bio=True)
    d.to_csv("E:/data/Sesj3/politics_new.csv", index=False)


def run():
    # Create new sample from a main category file
    d = utils.get_df(source=SESSION + "twp_corpus_politics.csv",
                     dt=True, drop_nans=True, drop_duplicates=True,
                     has_image=True, drop_missing_bio=True)
    data = sample_n_per_year(d, n=400, sp=SESSION + "data_new.csv")

    # Copy and resize images from the created sample
    preprocess_images.run(SESSION, target_size=(500, 500))

    def image_features_exists():
        if not os.path.exists(SESSION + "openimaj-images-all.csv"):
            input("Image features must be extracted \n Extract them and press the return key")
            return image_features_exists()
            # raise OSError(f"Missing file {SESSION + 'openimaj-images-all.csv'}")

    image_features_exists()

    # data = utils.get_df(SESSION + "data_new_plain.csv", dt=True)

    similarity_functions.run(SESSION, data)

    metric_combiner.run(SESSION,
                        ["title", "text", "image", "author", "author_bio", "time", "subcategory"])

    quantiles.run(SESSION)


if __name__ == '__main__':
    ospaths = definitions.get_paths()
    SESSION = "Final"
    SESSION = ospaths["datadir"] + SESSION + "/"
    print(f"Session: {SESSION}")
    run()
