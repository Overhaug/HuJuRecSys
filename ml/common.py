#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Functions common to several features
"""
import math
import sys
from datetime import timedelta, datetime

import pandas as pd
import pylcs
from Levenshtein import distance
from ngram import NGram
from nltk import SnowballStemmer
from nltk.corpus import stopwords
from nltk.metrics.distance import jaccard_distance
from pyjarowinkler.distance import get_jaro_distance
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from textblob import TextBlob

import utils


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
    # df_copy[feature] = df_copy[feature].apply(lambda x: x.split())
    df_copy[feature] = stemming_and_stopwords(df_copy[feature])
    print("Performing vectorization")
    return TfidfVectorizer().fit_transform(df_copy[feature])


def stemming_and_stopwords(text):
    stemmer = SnowballStemmer("english")
    stop = stopwords.words("english")
    text = text.apply(lambda x: x.split())
    # text = text.apply(lambda word_list: [w for w in word_list if w not in stop])
    return text.apply(lambda word_list: " ".join([stemmer.stem(w) for w in word_list if w not in stop]))


def remove_stopwords(text):
    stop = stopwords.words("english")
    text = text.apply(lambda x: x.split())
    return text.apply(lambda word_list: " ".join([w for w in word_list if w not in stop]))


def levenshtein(sp, df, feature, db):
    print(f"Computing Levenshtein distance on {feature}")
    text = df[feature]

    def normalized_levenshtein(s1, s2):
        max_len = max(len(s1), len(s2))
        return float(max_len - distance(s1, s2)) / float(max_len)

    if db:
        result = for_db(text, df, normalized_levenshtein)
    else:
        result = for_pivot(text, df, normalized_levenshtein)
    print()
    save_scores(result, sp=sp, db=db)
    print("_" * 100)


def jaro_winkler(sp, df, feature, db):
    print(f"Computing Jaro-Winkler on {feature}")
    text = df[feature]

    if db:
        result = for_db(text, df, get_jaro_distance)
    else:
        result = for_pivot(text, df, get_jaro_distance)
    print()
    save_scores(result, sp=sp, db=db)
    print("_" * 100)


def jaccard(sp, df, feature, db):
    print(f"Computing Jaccard distance on {feature}")
    text = df[feature]

    def compute(s1, s2):
        s1 = s1.split(" ")
        s2 = s2.split(" ")
        s1 = set(filter(None, s1))
        s2 = set(filter(None, s2))
        return jaccard_distance(s1, s2)

    if db:
        result = for_db(text, df, compute)
    else:
        result = for_pivot(text, df, compute)
    print()
    save_scores(result, sp=sp, db=db)
    print("_" * 100)


def longest_common_subsequence(sp, df, feature, db):
    print(f"Computing Longest Common Sequence distance on {feature}")
    text = df[feature]

    def compute_normalized(s1, s2):
        max_len = max(len(s1), len(s2))
        lcs = pylcs.lcs(s1, s2).__float__()
        return 1 - float(max_len - lcs) / float(max_len)

    if db:
        results = for_db(text, df, compute_normalized)
    else:
        results = for_pivot(text, df, compute_normalized)
    print()
    save_scores(results, sp=sp, db=db)
    print("_" * 100)
    return


def week_distance(sp, df, feature, db):
    print(f"Computing time distance on {feature}")
    df["datetime"] = concat_date_time(df)

    def compute(s1, s2):
        """
           Computes similarity between two timestamps (s1, s2)
        """
        s1 = s1.weekofyear
        s2 = s2.weekofyear
        largest = max(s1, s2)
        smallest = min(s1, s2)
        td = largest - smallest
        factor = 1 / 1.2
        try:
            weight = 1.0 * (factor ** math.sqrt(td))
        except ZeroDivisionError:
            weight = 1.0
        return smallest / largest

    if db:
        results = for_db(df["datetime"], df, compute)
    else:
        results = for_pivot(df["datetime"], df, compute)
    print()
    save_scores(results, sp=sp, db=db)
    print("_" * 100)


def concat_date_time(df):
    df["date"] = df["date"].apply(lambda t: t.strftime(format="%Y-%m-%d"))
    df["time"] = df["time"].apply(lambda t: t.strftime(format="%H:%M:%S"))
    return pd.to_datetime(df["date"] + " " + df["time"])


def exp_time_decay(sp, df, feature, db):
    print(f"Computing exponential time decay")
    df["datetime"] = concat_date_time(df)

    def compute(s1, s2):
        """
           Exponential time decay with a low factor.
        """
        largest = max(s1, s2)
        smallest = min(s1, s2)
        td = largest - smallest
        factor = 0.95
        return 1.0 * (factor ** math.sqrt(td.days))

    if db:
        results = for_db(df["datetime"], df, compute)
    else:
        results = for_pivot(df["datetime"], df, compute)
    print()
    save_scores(results, sp=sp, db=db)
    print("_" * 100)


def textblob_scores(sp, df, feature, db, score_type: tuple):
    """
        :param score_type must be a tuple of either "0, sentiment", or "1, subjectivity"
    """
    if not score_type == (0, "sentiment") and not score_type == (1, "subjectivity"):
        raise ValueError(f"arg {score_type} must be a tuple of either '0, sentiment', or '1, subjectivity'")
    print(f"Computing {score_type[1]} on {feature}")
    text = df[feature]

    def compute_normalize(s):
        return (TextBlob(s).sentiment[score_type[0]] + 1) / 2

    def compute(s):
        return TextBlob(s).sentiment[score_type[0]]

    func = compute
    if score_type[1] == "sentiment":
        func = compute_normalize

    results = for_dataframe(text, df, score_type[1], feature, func)
    print()
    save_scores(results, sp=sp, db=db)
    print("_" * 100)


def n_gram(sp, df, feature, db, n):
    print(f"Computing n-gram by a factor of {n} on {feature}")
    titles = df[feature]

    def compute(s1, s2):
        return NGram.compare(s1, s2, N=n)

    if db:
        results = for_db(titles, df, compute)
    else:
        results = for_pivot(titles, df, compute)
    print()
    save_scores(results, sp=sp, db=db)
    print("_" * 100)


def calculate_distance(f1, f2):
    """
        Calculate similarity distance between two positive floats
    """
    return min(f1, f2) / max(f1, f2)


def compute_distance(df, sp, feature, db):
    print(f"Computing distance similarity for {feature}")
    if not isinstance(df, pd.DataFrame):
        measures = utils.get_df(df)
    else:
        measures = df
    if db:
        results = for_db(measures[feature], measures, calculate_distance)
    else:
        results = for_pivot(measures[feature], measures, calculate_distance)
    print()
    save_scores(results, sp=sp, db=db)
    print("_" * 100)


def for_pivot(data, df, func):
    """
        Function to create pivot-applicable data
        :param func must be a function that takes two comparable arguments
    """
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=ids)
    scores["id"] = ids
    for i in range(0, len(df)):
        first = data[i]
        scores[ids[i]] = data.apply(lambda second: func(first, second))
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    return scores


def for_db(data, df, func):
    """
            Function to create db-insertable data
            :param func must be a function that takes two comparable arguments
    """
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=["id", "score", "referred_id"])
    for i in range(0, len(data)):
        first = data[i]
        td = data.apply(lambda second: func(first, second))
        scores = scores.append(
            [pd.DataFrame({"id": [ids[i] for _ in range(len(df))], "score": td, "referred_id": ids})],
            ignore_index=True)
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    return scores


def for_dataframe(data, df, score_name, feature, func):
    data = pd.DataFrame({feature: data})
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=["id"], data=ids)
    scores[score_name] = data[feature].apply(lambda i: func(i))
    return scores


def save_scores(scores, sp, db):
    if db:
    #     p = sp[:sp.rfind("/") + 1]
    #     s = sp[sp.rfind("/") + 1:]
    #     sp = p + "db-" + s
    # else:
    #     p = sp[:sp.rfind("/") + 1]
    #     s = sp[sp.rfind("/") + 1:]
    #     sp = p + "pivot-" + s
        scores = scores.pivot_table(index="id")
    scores.to_csv(sp)
    print(f"Saved scores to {sp}")
