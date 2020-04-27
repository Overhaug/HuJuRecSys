#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for extracting statistics from features
"""

import numpy as np
import pandas as pd

import definitions
import utils


def basic_words(data, description, feature, sep=None):
    """
    Do mean, median, min, and max for feature on data
    """
    methods = ["Mean", "Median", "Min", "Max"]
    stats = pd.DataFrame()
    stats["counts"] = data[feature].str.split(sep).apply(len)
    for m in methods:
        stats[m] = stats["counts"].apply(m.lower()).round(2)
    stats["Feature"] = description
    return pd.DataFrame(stats.drop("counts", axis=1).iloc[0]).transpose()


def chars(d, description, feature):
    methods = ["Mean", "Median", "Min", "Max"]
    stats = pd.DataFrame()
    stats["counts"] = d[feature].apply(len)
    for m in methods:
        stats[m] = stats["counts"].apply(m.lower()).round(2)
    stats["Feature"] = description
    return pd.DataFrame(stats.drop("counts", axis=1).iloc[0]).transpose()


def date(d, description):
    """
    Converts datetime to unix in order to find mean, median, min, and max
    """
    methods = ["Mean", "Median", "Min", "Max"]
    stats = pd.DataFrame()
    stats["date"] = pd.to_datetime(d["datetime"]).values.astype(np.int64)
    for m in methods:
        # stats[m] = d["datetime"].apply(m.lower())
        stats[m] = stats["date"].apply(m.lower()).round(2)
        stats[m] = pd.DataFrame(pd.to_datetime(stats[m]))
    stats["Feature"] = description
    stats["date"] = pd.DataFrame(pd.to_datetime(stats["date"], format="%Y-%m-%d %H:%M:%S"))
    return pd.DataFrame(stats.drop("date", axis=1).iloc[0]).transpose()


def basic_numerical(d, description, feature):
    """
    For calculating mean, median, min, and max for any strictly numerical values
    """
    methods = ["Mean", "Median", "Min", "Max"]
    stats = d
    for m in methods:
        stats[m] = stats[feature].apply(m.lower()).round(2)
    stats["Feature"] = description
    return pd.DataFrame(stats.drop(["id", feature], axis=1).iloc[0]).transpose()


def subcats(d):
    uniques = d["subcategory"].unique().tolist()
    subs = dict.fromkeys(uniques, 0)
    for u in uniques:
        counts = len(d.loc[d.subcategory == u])
        subs[u] = counts
    stats = pd.DataFrame({"Subcategory": list(subs.keys()), "Number of articles": list(subs.values())}) \
        .sort_values(by="Number of articles", ascending=False)
    return stats


def extract():
    # No of words title
    words_title_desc = "Number of words in the title"
    words_title = basic_words(df, words_title_desc, "title")

    # No of chars in title
    chars_title_desc = "Number of characters in the title"
    chars_title = chars(df, chars_title_desc, "title")

    # Image brightness
    brightness_desc = "Article image brightness"
    df_brightness = utils.get_for_feature(openimaj, "brightness")
    brightness = basic_numerical(df_brightness, brightness_desc, "brightness")

    # Image sharpness
    sharpness_desc = "Article image sharpness"
    df_sharpness = utils.get_for_feature(openimaj, "sharpness")
    sharpness = basic_numerical(df_sharpness, sharpness_desc, "sharpness")

    # Image contrast
    contrast_desc = "Article image contrast"
    df_contrast = utils.get_for_feature(openimaj, "contrast")
    contrast = basic_numerical(df_contrast, contrast_desc, "contrast")

    # Image colorfulness
    colorfulness_desc = "Article image colorfulness"
    df_colorfulness = utils.get_for_feature(openimaj, "colorfulness")
    colorfulness = basic_numerical(df_colorfulness, colorfulness_desc, "colorfulness")

    # Image entropy
    entropy_desc = "Article image entropy"
    df_entropy = utils.get_for_feature(openimaj, "entropy")
    entropy = basic_numerical(df_entropy, entropy_desc, "entropy")

    # No of authors
    no_authors_desc = "Number of authors"
    no_authors = basic_words(df, no_authors_desc, "author", sep=";")

    # No of words auth bios
    words_authbios_desc = "Number of words in author bios"
    words_authbios = basic_words(df, words_authbios_desc, "author_bio")

    # No of chars auth bios
    chars_authbios_desc = "Number of characters in author bios"
    chars_authbios = chars(df, chars_authbios_desc, "author_bio")

    # No of words text
    words_text_desc = "Number of words in article body text"
    words_text = basic_words(df, words_text_desc, "text")

    # No of chars text
    chars_text_desc = "Number of characters in article body text"
    chars_text = chars(df, chars_text_desc, "text")

    # Date of publication
    dop_desc = "Date of publication"
    dop = date(df, dop_desc)

    # Sentiment
    sent_desc = "Article body text sentiment"
    df_sent = utils.get_df(sentiment)
    sent = basic_numerical(df_sent, sent_desc, "sentiment")

    # Subcategory
    cats = subcats(df)
    cats.to_csv(SESSION + "politics_stats.csv", index=False)

    stats = pd.concat([words_title, chars_title, brightness, sharpness, contrast, colorfulness, entropy,
                       no_authors, words_authbios, chars_authbios, words_text, chars_text, dop, sent])

    cols = stats["Feature"]
    stats.drop(labels=["Feature"], axis=1, inplace=True)
    stats.insert(0, "Feature", cols)

    stats.to_csv(SESSION + "feature_stats.csv", index=False)
    print()


if __name__ == '__main__':
    SESSION = definitions.get_paths()["datadir"] + "Final/"
    openimaj = SESSION + "openimaj-images-all.csv"
    sentiment = SESSION + "text-sentiment.csv"
    sf = SESSION + "data_new_plain.csv"
    df = utils.get_df(sf, dt=True)

    extract()
