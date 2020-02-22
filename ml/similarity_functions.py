#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from twpc import utils

main_file = 'E:\\data\\corpus_wo_breaklines.csv'
politics_file = 'E:\\data\\stratified_politics_sample.csv'


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
    df['processed'] = df['processed'].apply(lambda x: [w for w in x if w not in stop])
    df['processed'] = df['processed'].apply(lambda x: ' '.join([stemmer.stem(w) for w in x]))

    tfidf = TfidfVectorizer().fit_transform(df.processed)
    ids = df.id.tolist()
    tfidf_df = pd.DataFrame(columns=ids)
    tfidf_df['id'] = ids

    for i in range(0, len(df)):
        cosine_similarities = linear_kernel(tfidf[i:i + 1], tfidf).flatten()
        this_id = df.loc[df.index[i], 'id']
        tfidf_df[this_id] = cosine_similarities

    if pivot:
        table = tfidf_df.pivot_table(index='id')
        table.to_csv("E:\\data\\tfidf_pivot.csv")
        return


if __name__ == '__main__':
    df = utils.get_df(politics_file, drop_nans=False)
    tf_idf(pivot=True)

# related_docs_indices = cosine_similarities.argsort()[:-6:-1]
