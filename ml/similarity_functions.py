#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module for computing item similarity across n-length set of documents and image feature vectors
"""
import os
import sys

import pandas as pd
from Levenshtein import distance
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from pyjarowinkler.distance import get_jaro_distance
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import normalize

from twpc import utils


# Implement all Similarity functions, which are:
# TODO: TITLE - Levenshtein Distance (DONE), Jaro-Winkler distance (DONE), Longest common subsequence, Bi-gram, LDA
# TODO: TEXT - TFIDF (DONE), BM25(?), LDA(?)
# TODO: IMAGES - Sharpness, Brightness, Contrast, Entropy distance, Embedding cosine similarity (DONE)
# TODO: DATE -
# TODO: TIME - Some distance measure
# TODO: AUTHOR - ?
# TODO: AUTHOR BIO - Similar measure as with title, due to its inherent short length?


def jaccard(a, b):
    a = set(a.split(" "))
    b = set(b.split(" "))
    union = a.union(b)
    intersection = a.intersection(b)
    return len(intersection) / len(union)


def tf_idf_cosine_sim(sp, feature):
    print(f"Computing cosine similarity-based TF-IDF on {feature}")
    stemmer = SnowballStemmer("english")
    stop = stopwords.words("english")
    print("Performing stopwords removal and stemming")
    tfidf_copy = df.copy()
    tfidf_copy[feature] = tfidf_copy[feature].apply(lambda x: x.split())
    tfidf_copy[feature] = tfidf_copy[feature].apply(lambda word_list: [w for w in word_list if w not in stop])
    tfidf_copy[feature] = tfidf_copy[feature].apply(lambda word_list: " ".join([stemmer.stem(w) for w in word_list]))
    print("Performing vectorization")
    vectors = TfidfVectorizer().fit_transform(df.text)

    scores = cosine_similarity(vectors)
    save_scores_as_pivot(scores, sp)
    print("_" * 100)
    return scores


def embeddings_cosine_sim(file, sp):
    print("Computing cosine similarity across image embeddings")
    id_embeddings = utils.get_out_file(file)
    embeddings = id_embeddings["embedding"].tolist()
    print("Normalizing image embeddings")
    normalized_embeddings = normalize(embeddings)

    scores = cosine_similarity(normalized_embeddings)
    save_scores_as_pivot(scores, sp)
    print("_" * 100)
    return scores


def jaro_winkler(sp, feature):
    print(f"Computing Jaro-Winkler on {feature}")
    titles = df[feature]
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=ids)
    scores["id"] = ids
    for i in range(0, len(titles)):
        first = titles[i]
        this_id = df.loc[df.index[i], "id"]
        scores[this_id] = titles.apply(lambda second: get_jaro_distance(first, second, winkler=True))
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    print()
    save_scores_as_pivot(scores, sp)
    print("_" * 100)
    return scores


def levenshtein(sp, feature):
    print(f"Computing Levenshtein distance on {feature}")
    titles = df[feature]
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=ids)
    scores["id"] = ids
    for i in range(0, len(titles)):
        first = titles[i]
        this_id = df.loc[df.index[i], "id"]
        # scores[this_id] = titles.apply(lambda a_title: distance(title, a_title))
        scores[this_id] = titles.apply(lambda second: normalized_levenshtein(first, second))
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    print()
    save_scores_as_pivot(scores, sp)
    print("_" * 100)
    return scores


def normalized_levenshtein(first, second):
    max_len = max(len(first), len(second))
    return float(max_len - distance(first, second)) / float(max_len)


def cosine_similarity(vectors):
    print("Computing cosine similarity")
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=ids)
    scores["id"] = ids
    for i in range(0, len(df)):
        cosine_similarities = linear_kernel(vectors[i:i + 1], vectors).flatten()
        this_id = df.loc[df.index[i], "id"]
        scores[this_id] = cosine_similarities
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    print()
    return scores


def save_scores_as_pivot(scores, sp):
    table = scores.pivot_table(index="id")
    sp = sp[:sp.rfind(".")] + "-pivot.csv"
    table.to_csv(sp)
    print(f"Saved scores to {sp}")


def load_scores():
    embeddings = utils.get_pivot(session + "embedding-cosine-scores-pivot.csv")
    tfidfs = utils.get_pivot(session + "tfidf-cosine-scores-pivot.csv")
    jw = utils.get_pivot(session + "jw-scores-pivot.csv")
    lev = utils.get_pivot(session + "norm-levenshtein-scores-pivot.csv")
    return embeddings, tfidfs, jw, lev


def mean_scores(sp):
    emb, tfidf, jw, lev = load_scores()
    scores = pd.concat((emb, tfidf, lev))
    by_row = scores.groupby(scores.index)
    df_means = by_row.mean()
    save_scores_as_pivot(df_means, sp)
    return df_means


def compute():
    # tf_idf_cosine_sim(session + "tfidf-cosine-scores.csv", save_as="pivot")
    # embeddings_cosine_sim(session + "VGG16-embeddings.out", session + "embedding-cosine-scores.csv", save_as="pivot")
    # jaro_winkler(session + "jw-scores.csv", "title")
    levenshtein(session + "norm-levenshtein-scores.csv", "title")


def create_embeddings():
    if os.path.exists(session + "id_path.csv") and not os.path.exists(session + "VGG16-embeddings.out"):
        print("Embedding images in current session")
        from images.image_embeddings import embed_vgg16
        idpath = session + "id_path.csv"
        paths = pd.read_csv(idpath)
        embed_vgg16(paths['path'].values, path=session + "VGG16-embeddings.out")


if __name__ == '__main__':
    base = "E:/data/"
    session = base + "27-02-2020-14-16" + "/"
    print(f"Session directory: {session}")
    create_embeddings()
    sf = session + "sample_Politics_400_plain.csv"
    df = utils.get_df(sf, drop_nans=False)
    # compute()
    mean_scores(session + "mean_scores-lev.csv")
