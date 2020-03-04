#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for computing item similarity across n-length set of documents and image feature vectors
"""

import pandas as pd

import common
import time_similarity
from definitions import get_paths
from twpc import utils
from wrappers import bio_similarity, text_similarity, title_similarity, image_similarity

TITLE = "title"
TEXT = "text"
AUTHOR_BIO = "author_bio"
IMAGE = "image"
TIME = "time"
DATE = "date"


def load_scores():
    scores = [utils.get_pivot(session + "pivot-embeddings-cs.csv"),
              utils.get_pivot(session + "pivot-text-tfidf-cs.csv"),
              utils.get_pivot(session + "pivot-bio-levenshtein.csv"),
              utils.get_pivot(session + "pivot-title-lcs.csv")]
    return scores


def mean_scores():
    scores = load_scores()
    scores = pd.concat(scores)
    by_row = scores.groupby(scores.index)
    df_means = by_row.mean()
    sp = session + "mean-scores-" + "-".join(["emb", "textTFIDF", "bioLV", "titleLCS", ".csv"])
    common.save_scores(df_means, sp, False)
    return df_means


def compute(db):
    if TITLE in settings:
        if "lev" in settings[TITLE]:
            title_similarity.title_levenshtein(session + "title-levenshtein.csv", df, db)
        if "jw" in settings[TITLE]:
            title_similarity.title_jw(session + "title-jarowinkler.csv", df, db)
        if "lcs" in settings[TITLE]:
            title_similarity.title_lcs(session + "title-lcs.csv", df, db)
    if TEXT in settings:
        if "tfidf" in settings[TEXT]:
            text_similarity.text_tfidf_cosine_sim(session + "text-tfidf-cs.csv", df, db)
    if IMAGE in settings:
        if "emb" in settings[IMAGE]:
            image_similarity.embeddings_cosine_sim(session + "VGG16-embeddings.out",
                                                   session + "embeddings-cs.csv", df, db)
    if AUTHOR_BIO in settings:
        if "tfidf" in settings[AUTHOR_BIO]:
            bio_similarity.bio_tfidf_cosine_sim(session + "bio-tfidf-cs.csv", df, db)
        if "jaccard" in settings[AUTHOR_BIO]:
            bio_similarity.bio_jaccard(session + "bio-jaccard.csv", df, db)
        if "lev" in settings[AUTHOR_BIO]:
            bio_similarity.bio_levenshtein(session + "bio-levenshtein.csv", df, db)
    if TIME in settings:
        if "tdelta" in settings[TIME]:
            time_similarity.time_distance(session + "time-tdelta.csv", df, db)


if __name__ == '__main__':
    ospaths = get_paths()
    session = "27-02-2020-14-16"
    session = ospaths["datadir"] + session + "/"
    print(f"Session directory: {session}")
    sf = session + "sample_Politics_400_plain.csv"
    # df = utils.get_df(sf, drop_nans=False, dt=True)
    settings = {
        #TITLE: ["lev", "jw", "lcs"],
        #TEXT: ["tfidf"],
        #IMAGE: ["emb"],
        #AUTHOR_BIO: ["lev", "tfidf", "jaccard"],
        TIME: ["tdelta"]

    }
    # compute(db=False)
    mean_scores()
