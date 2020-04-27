#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for combing various similarity metrics
    Filenames are hard-coded because similarity metrics are always created with the same filename.
    The only change is the SESSION variable
"""
import sys

import pandas as pd

import utils

SESSION = ""


# todo: create a definitions module to universify filenames. Can then be used from any module to grab any file


def mean_scores(metrics):
    data = []
    if "title" in metrics:
        data += all_title()
    if "text" in metrics:
        data += all_text()
    if "author" in metrics:
        data += all_author()
    if "author_bio" in metrics:
        data += all_authorbio()
    if "image" in metrics:
        data += all_image()
    if "time" in metrics:
        data += all_time()
    if "subcategory" in metrics:
        data += all_category()

    all_scores = pd.concat(data)
    formatted_scores = pd.DataFrame(columns=["first", "second", "score"])
    ids = all_scores.columns
    by_row = all_scores.groupby(all_scores.index)
    df_means = by_row.mean()
    scores_length = len(df_means)
    for i, column in enumerate(df_means.columns.values):
        temp = pd.DataFrame()
        temp["first"] = [column for _ in range(scores_length)]
        temp["second"] = ids
        temp["score"] = df_means[column].values
        formatted_scores = pd.concat([formatted_scores, temp])
        sys.stdout.write("\r" + f"{i + 1}/{scores_length}")
    sp = SESSION + "mean-scores.csv"
    formatted_scores.to_csv(sp, index=False)
    print(" \n Saved mean scores")


def all_title():
    return [utils.get_pivot(SESSION + "title-levenshtein.csv"),
            utils.get_pivot(SESSION + "title-jarowinkler.csv"),
            utils.get_pivot(SESSION + "title-lcs.csv"),
            utils.get_pivot(SESSION + "title-ngram.csv"),
            utils.get_pivot(SESSION + "title-lda.csv")]


def all_text():
    return [utils.get_pivot(SESSION + "text-sentiment-sim.csv"),
            utils.get_pivot(SESSION + "text-lda.csv"),
            utils.get_pivot(SESSION + "text-tfidf-cs.csv"),
            utils.get_pivot(SESSION + "text-tfidf-cs-constr.csv")]


def all_image():
    return [utils.get_pivot(SESSION + "sharpness-sim.csv"),
            utils.get_pivot(SESSION + "entropy-sim.csv"),
            utils.get_pivot(SESSION + "brightness-sim.csv"),
            utils.get_pivot(SESSION + "colorfulness-sim.csv"),
            utils.get_pivot(SESSION + "contrast-sim.csv"),
            utils.get_pivot(SESSION + "embeddings-cs.csv")]


def all_authorbio():
    return [utils.get_pivot(SESSION + "bio-tfidf-cs.csv"),
            utils.get_pivot(SESSION + "bio-lda.csv")]


def all_author():
    return [utils.get_pivot(SESSION + "author-jaccard.csv")]


def all_time():
    return [  # utils.get_pivot(SESSION + "exp-decay.csv"),
        utils.get_pivot(SESSION + "days-distance-similarity.csv")]


def all_category():
    return [utils.get_pivot(SESSION + "category-jaccard.csv")]


def run(session_name, combination):
    print(f"Combining metrics '{combination}'")
    global SESSION
    SESSION = session_name
    mean_scores(combination)
