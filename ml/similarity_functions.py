#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from twpc import utils



# Implement all Similarity functions, which are:
# TODO: TITLE - Levenshtein Distance, Jaro-Winkler distance, Longest common subsequence, Bi-gram, LDA
# TODO: TEXT - TFIDF (DONE), BM25(?), LDA(?)
# TODO: IMAGES - Sharpness, Brightness, Contrast, Entropy distance, Embedding cosine similarity
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


def tf_idf(pivot=True):
    stemmer = SnowballStemmer("english")
    stop = stopwords.words("english")
    df['processed'] = df['text'].apply(lambda x: x.split())
    df['processed'] = df['processed'].apply(lambda word_list: [w for w in word_list if w not in stop])
    df['processed'] = df['processed'].apply(lambda word_list: ' '.join([stemmer.stem(w) for w in word_list]))

    vectors = TfidfVectorizer().fit_transform(df.processed)
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=ids)
    scores['id'] = ids

    for i in range(0, len(df)):
        cosine_similarities = linear_kernel(vectors[i:i + 1], vectors).flatten()
        this_id = df.loc[df.index[i], 'id']
        scores[this_id] = cosine_similarities

    if pivot:
        table = scores.pivot_table(index='id')
        table.to_csv("E:/data/tfidf_pivot.csv")
        return


if __name__ == '__main__':
    politics_file = 'E:/data/stratified_politics_sample_html_plain.csv'
    df = utils.get_df(politics_file, drop_nans=False)
    tf_idf(pivot=True)
# related_docs_indices = cosine_similarities.argsort()[:-6:-1]
