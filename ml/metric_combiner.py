#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for combing various similarity metrics
"""
import sys

import pandas as pd

import utils
from definitions import get_paths


def mean_scores(metrics):
    data = []
    if "all" in metrics:
        data += all_title()
        data += all_image()
        data += all_text()
        data += all_time()
        data += all_author()
        data += all_authorbio()
    elif "title" in metrics:
        data += all_title()
    elif "text" in metrics:
        data += all_text()
    elif "author" in metrics:
        data += all_author()
    elif "authorbio" in metrics:
        data += all_authorbio()
    elif "image" in metrics:
        data += all_image()
    elif "time" in metrics:
        data += all_time()

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
    print("Saved mean scores")


def all_title():
    return [utils.get_pivot(SESSION + "title-levenshtein.csv"),
            utils.get_pivot(SESSION + "title-jarowinkler.csv"),
            utils.get_pivot(SESSION + "title-lcs.csv"),
            utils.get_pivot(SESSION + "title-ngram.csv"),
            utils.get_pivot(SESSION + "title-lda.csv")]


def all_text():
    return [utils.get_pivot(SESSION + "text-subjectivity-sim.csv"),
            utils.get_pivot(SESSION + "text-sentiment-sim.csv"),
            utils.get_pivot(SESSION + "text-lda.csv"),
            utils.get_pivot(SESSION + "text-tfidf-cs.csv"),
            utils.get_pivot(SESSION + "text-tfidf-cs-constr.csv")]


def all_image():
    return [utils.get_pivot(SESSION + "sharpness-sim.csv"),
            utils.get_pivot(SESSION + "shannon-sim.csv"),
            utils.get_pivot(SESSION + "brightness-sim.csv"),
            utils.get_pivot(SESSION + "colorfulness-sim.csv"),
            utils.get_pivot(SESSION + "contrast-sim.csv")]


def all_authorbio():
    return [utils.get_pivot(SESSION + "bio-jaccard.csv"),
            utils.get_pivot(SESSION + "bio-levenshtein.csv"),
            utils.get_pivot(SESSION + "bio-tfidf-cs.csv")]


def all_author():
    return [utils.get_pivot(SESSION + "author-jaccard.csv")]


def all_time():
    return [utils.get_pivot(SESSION + "exp-decay.csv")]


ospaths = get_paths()
SESSION = "Sesj2"
SESSION = ospaths["datadir"] + SESSION + "/"
print(f"Session directory: {SESSION}")
mean_scores(["all"])
