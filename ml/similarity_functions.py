#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for computing item similarity across n-length set of documents and image feature vectors
"""
import sys

import pandas as pd

import author_similarity
import common
from definitions import get_paths
from twpc import utils
from wrappers import bio_similarity, text_similarity, title_similarity, image_similarity, time_similarity

TITLE = "title"
TEXT = "text"
AUTHOR_BIO = "author_bio"
AUTHOR = "author"
IMAGE = "image"
TIME = "time"
DATE = "date"
IMAGE_FEATURE_COLLECTION = "openimaj-images.csv"


def load_scores():
    scores = [utils.get_pivot(SESSION + "title-levenshtein.csv"),
              utils.get_pivot(SESSION + "title-jarowinkler.csv"),
              utils.get_pivot(SESSION + "title-lcs.csv"),
              utils.get_pivot(SESSION + "ngram-lcs.csv"),
              utils.get_pivot(SESSION + "text-subjectivity-sim.csv"),
              utils.get_pivot(SESSION + "text-sentiment-sim.csv"),
              utils.get_pivot(SESSION + "text-lda.csv"),
              utils.get_pivot(SESSION + "sharpness-sim.csv"),
              utils.get_pivot(SESSION + "shannon-sim.csv"),
              utils.get_pivot(SESSION + "brightness-sim.csv"),
              utils.get_pivot(SESSION + "colorfulness-sim.csv"),
              utils.get_pivot(SESSION + "contrast-sim.csv"),
              utils.get_pivot(SESSION + "bio-jaccard.csv"),
              utils.get_pivot(SESSION + "bio-levenshtein.csv"),
              # utils.get_pivot(SESSION + "week-similarity.csv"),
              utils.get_pivot(SESSION + "exp-decay.csv")
              ]
    return scores


def mean_scores():
    scores = load_scores()
    scores = pd.concat(scores)
    new_scores = pd.DataFrame(columns=["first", "second", "score"])
    ids = scores.columns
    by_row = scores.groupby(scores.index)
    df_means = by_row.mean()
    scores_length = len(df_means)
    for i, column in enumerate(df_means.columns.values):
        temp = pd.DataFrame()
        temp["first"] = [column for _ in range(scores_length)]
        temp["second"] = ids
        temp["score"] = df_means[column].values
        new_scores = pd.concat([new_scores, temp])
        sys.stdout.write("\r" + f"{i + 1}/{scores_length}")
    sp = SESSION + "mean-scores.csv"
    new_scores.to_csv(sp, index=False)
    print("Saved mean scores")
    return df_means


def compute(update):
    print(f"Computing similarity for:")
    for i, v in metrics.items():
        print(f"{i}:", ', '.join(v))
    if TITLE in metrics:
        if "lev" in metrics[TITLE]:
            title_similarity.title_levenshtein(SESSION + "title-levenshtein.csv", df)
        if "jw" in metrics[TITLE]:
            title_similarity.title_jw(SESSION + "title-jarowinkler.csv", df)
        if "lcs" in metrics[TITLE]:
            title_similarity.title_lcs(SESSION + "title-lcs.csv", df)
        if "ngram" in metrics[TITLE]:
            title_similarity.title_ngram(SESSION + "ngram-lcs.csv", df, n=2)
        if "lda" in metrics[TITLE]:
            title_similarity.title_lda(SESSION + "title-lda.csv", df, SESSION, update)
    if TEXT in metrics:
        if "tfidf" in metrics[TEXT]:
            text_similarity.text_tfidf_cosine_sim(SESSION + "text-tfidf-cs.csv", df)
        if "tfidf_constr" in metrics[TEXT]:
            text_similarity.text_tfidf_cosine_sim_length_constrained(SESSION + "text-tfidf-cs-constr.csv", df, 400)
        if "subjectivity" in metrics[TEXT]:
            text_similarity.text_textblob(SESSION + "text-subjectivity.csv",
                                          SESSION + "text-subjectivity-sim.csv", df, (1, "subjectivity"), update)
        if "sentiment" in metrics[TEXT]:
            text_similarity.text_textblob(SESSION + "text-sentiment.csv",
                                          SESSION + "text-sentiment-sim.csv", df, (0, "sentiment"), update)
        if "lda" in metrics[TEXT]:
            text_similarity.text_lda(SESSION + "text-lda.csv", df, SESSION, update)
    if IMAGE in metrics:
        if "emb" in metrics[IMAGE]:

            image_similarity.embeddings_cosine_sim(SESSION + "VGG16-embeddings.out",
                                                   SESSION + "embeddings-cs.csv", df)
        image_similarity.preload(SESSION + "resized_images")  # Pre-load images for faster computation.
        if "sharpness" in metrics[IMAGE]:
            image_similarity.image_sharpness(SESSION + "sharpness.csv", SESSION + "sharpness-sim.csv", df, update)
        if "shannon" in metrics[IMAGE]:
            image_similarity.image_shannon(SESSION + "shannon.csv", SESSION + "shannon-sim.csv", df, update)
        image_similarity.clear()  # Free up memory
        if "brightness" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SESSION + "brightness-sim.csv", "brightness")
        if "colorfulness" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SESSION + "colorfulness-sim.csv", "colorfulness")
        if "contrast" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SESSION + "contrast-sim.csv", "contrast")
    if AUTHOR_BIO in metrics:
        if "tfidf" in metrics[AUTHOR_BIO]:
            bio_similarity.bio_tfidf_cosine_sim(SESSION + "bio-tfidf-cs.csv", df)
        if "jaccard" in metrics[AUTHOR_BIO]:
            bio_similarity.bio_jaccard(SESSION + "bio-jaccard.csv", df)
        if "lev" in metrics[AUTHOR_BIO]:
            bio_similarity.bio_levenshtein(SESSION + "bio-levenshtein.csv", df)
    if AUTHOR in metrics:
        if "jaccard" in metrics[AUTHOR]:
            author_similarity.author_jaccard(SESSION + "author-jaccard.csv", df)
    if TIME in metrics:
        if "week" in metrics[TIME]:
            time_similarity.time_week_distance(SESSION + "week-similarity.csv", df)
        if "exp_decay" in metrics[TIME]:
            time_similarity.time_exp_decay(SESSION + "exp-decay.csv", df)


if __name__ == '__main__':
    ospaths = get_paths()
    SESSION = "Sesj2"
    SESSION = ospaths["datadir"] + SESSION + "/"
    print(f"Session directory: {SESSION}")
    # sf = SESSION + "sample_Politics_400_plain.csv"
    sf = SESSION + "new_plain.csv"
    df = utils.get_df(sf, drop_nans=False, dt=True)
    metrics = {
        TITLE: ["lev", "jw", "lcs", "ngram", "lda"],
        TEXT: ["tfidf", "subjectivity", "sentiment", "lda", "tfidf_constr"],
        IMAGE: ["emb", "sharpness", "shannon", "brightness", "colorfulness", "contrast"],
        AUTHOR_BIO: ["lev", "tfidf", "jaccard"],
        TIME: ["exp_decay"],

    }
    compute(update=True)
    # mean_scores()
