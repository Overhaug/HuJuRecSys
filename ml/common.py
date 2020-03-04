#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Functions common to several features
"""

import sys

import pandas as pd
import pylcs
from Levenshtein import distance
from nltk import SnowballStemmer
from nltk.corpus import stopwords
from nltk.metrics.distance import jaccard_distance
from pyjarowinkler.distance import get_jaro_distance
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def cosine_similarity(sp, df, vectors, db):
    ids = df.id.tolist()
    print("Computing cosine similarity")

    def for_db():
        scores = pd.DataFrame(columns=["id", "score", "referred_id"])
        for i in range(0, len(df)):
            # cs = [1 - tf.losses.cosine_similarity(vectors[i], vectors[i:i + 1], axis=0) for _ in range(len(df))]
            cosine_similarities = linear_kernel(vectors[i:i + 1], vectors).flatten()
            this_id = ids[i]
            scores = scores.append(
                [pd.DataFrame(
                    {"id": [this_id for _ in range(len(df))], "score": cosine_similarities, "referred_id": ids})],
                ignore_index=True)
            sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
        return scores

    def for_pivot():
        scores = pd.DataFrame(columns=ids)
        scores["id"] = ids
        for i in range(0, len(df)):
            cosine_similarities = linear_kernel(vectors[i:i + 1], vectors).flatten()
            this_id = ids[i]
            scores[this_id] = cosine_similarities
            sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
        return scores

    if db:
        result = for_db()
    else:
        result = for_pivot()
    print()
    save_scores(result, sp=sp, db=db)
    print("_" * 100)


def tfidf(df, feature):
    print(f"Computing TFIDF on {feature}")
    print("Performing stopwords removal and stemming")
    df_copy = df.copy()
    df_copy[feature] = df_copy[feature].apply(lambda x: x.split())
    df_copy[feature] = stemming_and_stopwords(df_copy[feature])
    print("Performing vectorization")
    return TfidfVectorizer().fit_transform(df_copy[feature])


def stemming_and_stopwords(text):
    stemmer = SnowballStemmer("english")
    stop = stopwords.words("english")
    text = text.apply(lambda word_list: [w for w in word_list if w not in stop])
    return text.apply(lambda word_list: " ".join([stemmer.stem(w) for w in word_list]))


def levenshtein(sp, df, feature, db):
    print(f"Computing Levenshtein distance on {feature}")
    text = df[feature]

    def normalized_levenshtein(first, second):
        max_len = max(len(first), len(second))
        return float(max_len - distance(first, second)) / float(max_len)

    if db:
        result = compute_for_db(text, df, normalized_levenshtein)
    else:
        result = compute_for_pivot(text, df, normalized_levenshtein)
    print()
    save_scores(result, sp=sp, db=db)
    print("_" * 100)


def jaro_winkler(sp, df, feature, db):
    print(f"Computing Jaro-Winkler on {feature}")
    text = df[feature]

    if db:
        result = compute_for_db(text, df, get_jaro_distance)
    else:
        result = compute_for_pivot(text, df, get_jaro_distance)
    print()
    save_scores(result, sp=sp, db=db)
    print("_" * 100)


def jaccard(sp, df, feature, db):
    print(f"Computing Jaccard distance on {feature}")
    text = df[feature]

    def compute(a, b):
        a = a.split(" ")
        b = b.split(" ")
        a = set(filter(None, a))
        b = set(filter(None, b))
        return jaccard_distance(a, b)

    if db:
        result = compute_for_db(text, df, compute)
    else:
        result = compute_for_pivot(text, df, compute)
    print()
    save_scores(result, sp=sp, db=db)
    print("_" * 100)


def longest_common_subsequence(sp, df, feature, db):
    print(f"Computing Longest Common Sequence distance on {feature}")
    text = df[feature]

    def compute_normalized(first, second):
        max_len = max(len(first), len(second))
        lcs = pylcs.lcs(first, second).__float__()
        return 1 - float(max_len - lcs) / float(max_len)

    if db:
        results = compute_for_db(text, df, compute_normalized)
    else:
        results = compute_for_pivot(text, df, compute_normalized)
    print()
    save_scores(results, sp=sp, db=db)
    print("_" * 100)
    return


def time_distance(sp, df, feature, db):
    print(f"Computing time distance on {feature}")
    hours = df[feature].apply(lambda t: t.strftime(format="%H"))

    def compute(first, second):
        """
           Computes similarity between two timestamps (first, second)
        """
        if first == "00":
            first = "24"
        if second == "00":
            second = "24"
        max_len = max(int(first), int(second))
        min_len = min(int(first), int(second))
        td = max_len - min_len
        weight = 1
        if td > 11:
            weight = 0.8
        if td > 5:
            weight = 0.875
        if td > 2:
            weight = 0.95
        result = 1 - float(max_len - min_len * weight) / float(max_len)
        return result

    if db:
        results = compute_for_db(hours, df, compute)
    else:
        results = compute_for_pivot(hours, df, compute)
    print()
    save_scores(results, sp=sp, db=db)
    print("_" * 100)
    return


def compute_for_pivot(data, df, func):
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=ids)
    scores["id"] = ids
    for i in range(0, len(df)):
        first = data[i]
        this_id = ids[i]
        scores[this_id] = data.apply(lambda second: func(first, second))
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    return scores


def compute_for_db(data, df, func):
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=["id", "score", "referred_id"])
    for i in range(0, len(data)):
        first = data[i]
        this_id = ids[i]
        td = data.apply(lambda second: func(first, second))
        scores = scores.append(
            [pd.DataFrame({"id": [this_id for _ in range(len(df))], "score": td, "referred_id": ids})],
            ignore_index=True)
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    return scores


def save_scores(scores, sp, db):
    if db:
        p = sp[:sp.rfind("/") + 1]
        s = sp[sp.rfind("/") + 1:]
        sp = p + "db-" + s
    else:
        p = sp[:sp.rfind("/") + 1]
        s = sp[sp.rfind("/") + 1:]
        sp = p + "pivot-" + s
        scores = scores.pivot_table(index="id")
    scores.to_csv(sp)
    print(f"Saved scores to {sp}")
