#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for computing item similarity across n-length set of documents and image feature vectors
"""

from wrappers import bio_similarity, text_similarity, title_similarity, \
    image_similarity, time_similarity, category_similarity, author_similarity

TITLE = "title"
BODY_TEXT = "text"
AUTHOR_BIO = "author_bio"
AUTHOR = "author"
IMAGE = "image"
TIME = "time"
SUBCATEGORY = "subcategory"

IMAGE_FEATURE_COLLECTION = "openimaj-images-all.csv"

SIM_SESSION = ""
metrics = {}


def compute(df, update):
    print(f"Computing similarity for:")
    for i, v in metrics.items():
        print(f"{i}:", ', '.join(v))
    if TITLE in metrics:
        if "lev" in metrics[TITLE]:
            title_similarity.title_levenshtein(SIM_SESSION + "title-levenshtein.csv", df)
        if "jw" in metrics[TITLE]:
            title_similarity.title_jw(SIM_SESSION + "title-jarowinkler.csv", df)
        if "lcs" in metrics[TITLE]:
            title_similarity.title_lcs(SIM_SESSION + "title-lcs.csv", df)
        if "ngram" in metrics[TITLE]:
            title_similarity.title_ngram(SIM_SESSION + "title-ngram.csv", df, n=2)
        if "lda" in metrics[TITLE]:
            title_similarity.title_lda(SIM_SESSION + "title-lda.csv", df, SIM_SESSION, update)
    if BODY_TEXT in metrics:
        if "tfidf" in metrics[BODY_TEXT]:
            text_similarity.text_tfidf_cosine_sim(SIM_SESSION + "text-tfidf-cs.csv", df)
        if "tfidf_constr" in metrics[BODY_TEXT]:
            text_similarity.text_tfidf_cosine_sim_length_constrained(SIM_SESSION + "text-tfidf-cs-constr.csv", df, 50)
        if "subjectivity" in metrics[BODY_TEXT]:
            text_similarity.text_textblob(SIM_SESSION + "text-subjectivity.csv",
                                          SIM_SESSION + "text-subjectivity-sim.csv", df, (1, "subjectivity"), update)
        if "sentiment" in metrics[BODY_TEXT]:
            text_similarity.text_textblob(SIM_SESSION + "text-sentiment.csv",
                                          SIM_SESSION + "text-sentiment-sim.csv", df, (0, "sentiment"), update)
        if "lda" in metrics[BODY_TEXT]:
            text_similarity.text_lda(SIM_SESSION + "text-lda.csv", df, SIM_SESSION, update)
    if IMAGE in metrics:
        if "emb" in metrics[IMAGE]:
            image_similarity.embeddings_cosine_sim(SIM_SESSION + "VGG16-embeddings.out",
                                                   SIM_SESSION + "embeddings-cs.csv", df)
        if "entropy" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SIM_SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SIM_SESSION + "entropy-sim.csv", "entropy", True)
        if "sharpness" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SIM_SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SIM_SESSION + "sharpness-sim.csv", "sharpness", True)
        if "brightness" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SIM_SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SIM_SESSION + "brightness-sim.csv", "brightness", False)
        if "colorfulness" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SIM_SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SIM_SESSION + "colorfulness-sim.csv", "colorfulness",
                                                              False)
        if "contrast" in metrics[IMAGE]:
            image_similarity.image_calculate_computed_metrics(SIM_SESSION + IMAGE_FEATURE_COLLECTION,
                                                              SIM_SESSION + "contrast-sim.csv", "contrast", False)
    if AUTHOR_BIO in metrics:
        if "tfidf" in metrics[AUTHOR_BIO]:
            bio_similarity.bio_tfidf_cosine_sim(SIM_SESSION + "bio-tfidf-cs.csv", df)
        if "lda" in metrics[AUTHOR_BIO]:
            bio_similarity.bio_lda(SIM_SESSION + "bio-lda.csv", df, SIM_SESSION, update)
    if AUTHOR in metrics:
        if "jaccard" in metrics[AUTHOR]:
            author_similarity.author_jaccard(SIM_SESSION + "author-jaccard.csv", df)
    if TIME in metrics:
        if "days" in metrics[TIME]:
            time_similarity.time_days_distance(SIM_SESSION + "days-distance-similarity.csv", df)
    if SUBCATEGORY in metrics:
        if "jacc" in metrics[SUBCATEGORY]:
            category_similarity.subcategory_jacc(SIM_SESSION + "category-jaccard.csv", df)


def run(session_name, data):
    global SIM_SESSION, metrics
    SIM_SESSION = session_name
    metrics = {
        TITLE: ["lev", "jw", "lcs", "ngram", "lda"],
        BODY_TEXT: ["tfidf", "tfidf_constr", "sentiment", "lda"],
        IMAGE: ["entropy", "sharpness", "brightness", "colorfulness", "contrast"],
        AUTHOR_BIO: ["tfidf", "lda"],
        AUTHOR: ["jaccard"],
        TIME: ["days"],
        SUBCATEGORY: ["jacc"]
    }
    compute(data, update=True)
