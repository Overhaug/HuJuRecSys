#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for computing item similarity across n-length set of documents and image feature vectors
"""

import pandas as pd
import pprint

import common
from definitions import get_paths
from twpc import utils
from wrappers import bio_similarity, text_similarity, title_similarity, image_similarity, time_similarity

TITLE = "title"
TEXT = "text"
AUTHOR_BIO = "author_bio"
IMAGE = "image"
TIME = "time"
DATE = "date"
IMAGE_FEATURE_COLLECTION = "openimaj-images.csv"


def load_scores():
    scores = [utils.get_pivot(SESSION + "pivot-embeddings-cs.csv"),
              utils.get_pivot(SESSION + "pivot-text-tfidf-cs.csv"),
              utils.get_pivot(SESSION + "pivot-bio-levenshtein.csv"),
              utils.get_pivot(SESSION + "pivot-title-lcs.csv")]
    return scores


def mean_scores():
    scores = load_scores()
    scores = pd.concat(scores)
    by_row = scores.groupby(scores.index)
    df_means = by_row.mean()
    sp = SESSION + "mean-scores-" + "-".join(["emb", "textTFIDF", "bioLV", "titleLCS", ".csv"])
    common.save_scores(df_means, sp, False)
    return df_means


def compute(db, update):
    print(f"Computing similarity for:")
    for i, v in metrics.items():
        print(f"{i}:", ', '.join(v))
    if TITLE in metrics:
        if "lev" in metrics[TITLE]:
            title_similarity.title_levenshtein(SESSION + "title-levenshtein.csv", df, db)
        if "jw" in metrics[TITLE]:
            title_similarity.title_jw(SESSION + "title-jarowinkler.csv", df, db)
        if "lcs" in metrics[TITLE]:
            title_similarity.title_lcs(SESSION + "title-lcs.csv", df, db)
        if "ngram" in metrics[TITLE]:
            title_similarity.title_ngram(SESSION + "ngram-lcs.csv", df, db, n=2)
        if "lda" in metrics[TITLE]:
            title_similarity.title_lda(SESSION + "title-lda.csv", df, db, SESSION, update)
    if TEXT in metrics:
        if "tfidf" in metrics[TEXT]:
            text_similarity.text_tfidf_cosine_sim(SESSION + "text-tfidf-cs.csv", df, db)
        # Subjectivity and sentiment could be computed in the same run (which would be faster, too)
        # They are separated so it is more clear what they do.
        if "subjectivity" in metrics[TEXT]:
            text_similarity.text_textblob(SESSION + "text-subjectivity.csv",
                                          SESSION + "text-subjectivity-sim.csv", df, db, (1, "subjectivity"), update)
        if "sentiment" in metrics[TEXT]:
            text_similarity.text_textblob(SESSION + "text-sentiment.csv",
                                          SESSION + "text-sentiment-sim.csv", df, db, (0, "sentiment"), update)
        if "lda" in metrics[TEXT]:
            text_similarity.text_lda(SESSION + "text-lda.csv", df, db, SESSION, update)
    if IMAGE in metrics:
        if "emb" in metrics[IMAGE]:
            image_similarity.embeddings_cosine_sim(SESSION + "VGG16-embeddings.out",
                                                   SESSION + "embeddings-cs.csv", df, db)
        image_similarity.preload(SESSION + "images")  # Pre-load images for faster computation.
        if "sharpness" in metrics[IMAGE]:
            image_similarity.image_sharpness(SESSION + "sharpness.csv", SESSION + "sharpness-sim.csv", df, db, update)
        if "shannon" in metrics[IMAGE]:
            image_similarity.image_shannon(SESSION + "shannon.csv", SESSION + "shannon-sim.csv", df, db, update)
        image_similarity.clear()
        if "brightness" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SESSION + "brightness-sim.csv", "brightness", db)
        if "colorfulness" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SESSION + "colorfulness-sim.csv", "colorfulness", db)
        if "contrast" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SESSION + "contrast-sim.csv", "contrast", db)
    if AUTHOR_BIO in metrics:
        if "tfidf" in metrics[AUTHOR_BIO]:
            bio_similarity.bio_tfidf_cosine_sim(SESSION + "bio-tfidf-cs.csv", df, db)
        if "jaccard" in metrics[AUTHOR_BIO]:
            bio_similarity.bio_jaccard(SESSION + "bio-jaccard.csv", df, db)
        if "lev" in metrics[AUTHOR_BIO]:
            bio_similarity.bio_levenshtein(SESSION + "bio-levenshtein.csv", df, db)
    if TIME in metrics:
        if "week" in metrics[TIME]:
            time_similarity.time_week_distance(SESSION + "week-similarity.csv", df, db)
        if "exp_decay" in metrics[TIME]:
            time_similarity.time_exp_decay(SESSION + "exp-decay.csv", df, db)


if __name__ == '__main__':
    ospaths = get_paths()
    SESSION = "27-02-2020-14-16"
    SESSION = ospaths["datadir"] + SESSION + "/"
    print(f"Session directory: {SESSION}")
    sf = SESSION + "sample_Politics_400_plain.csv"
    df = utils.get_df(sf, drop_nans=False, dt=True)
    metrics = {
        # TITLE: ["lev", "jw", "lcs", "ngram", "lda"],
        # TEXT: ["tfidf", "subjectivity", "sentiment", "lda"],
        # IMAGE: ["emb", "sharpness", "shannon", "brightness", "colorfulness", "contrast"],
        # AUTHOR_BIO: ["lev", "tfidf", "jaccard"],
        # TIME: ["exp_decay"],
        TEXT: ["sentiment", "subjectivity"]
    }
    compute(db=False, update=True)
    # mean_scores()
