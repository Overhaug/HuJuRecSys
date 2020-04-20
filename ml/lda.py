#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from multiprocessing import freeze_support

import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import LdaMulticore
from gensim.similarities import MatrixSimilarity

import common


def create_dictionary(session, df, feature):
    print(f"Updating dictionary for feature {feature}")
    documents = df[feature]
    documents = common.remove_stopwords(documents).tolist()
    texts = [doc.split() for doc in documents]
    dictionary = Dictionary(texts)
    dictionary.save(session + "LDA-dictionary-" + feature + ".pk1")


def create_model(session, df, feature):
    print(f"Updating model for feature {feature}")
    freeze_support()
    dct = get_dict(feature, session)
    corpus = common.remove_stopwords(df[feature]).tolist()
    corpus = [doc.split() for doc in corpus]
    corpus = [dct.doc2bow(text) for text in corpus]
    dct = Dictionary.load(session + "LDA-dictionary-" + feature + ".pk1")
    lda_model = LdaMulticore(corpus=corpus, id2word=dct, workers=5)
    lda_model.save(session + "LDA-model-" + feature)


def cs_lda(sp, df, feature, session, update_model):
    print(f"Starting LDA ...")
    if update_model:
        session = session + "lda-" + feature
        if not os.path.exists(session):
            print(f"New directory: {session}")
            os.mkdir(session)
        session = session + "/"
        create_dictionary(session, df, feature)
        create_model(session, df, feature)
    else:
        session = session + "lda-" + feature
    print(f"Computing Cosine Similarity on feature {feature}")
    dct = get_dict(feature, session)
    corpus = common.remove_stopwords(df[feature]).tolist()
    corpus = [doc.split() for doc in corpus]
    corpus = [dct.doc2bow(text) for text in corpus]
    lda = LdaMulticore.load(session + "LDA-model-" + feature)
    res = lda[corpus]
    index = MatrixSimilarity(res)

    # index.save("simIndex.index")

    def compute(text):
        vec_bow = dct.doc2bow(text.split())
        vec_lda = lda[vec_bow]
        sims = index[vec_lda]
        return sims

    results = for_pivot(df[feature], df, compute)
    print()
    common.save_as_pivot(results, sp=sp)
    print("_" * 100)


def get_dict(feature, session):
    return Dictionary.load(session + "LDA-dictionary-" + feature + ".pk1")


def for_pivot(data, df, func):
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=ids)
    scores["id"] = ids
    for i in range(0, len(df)):
        scores[ids[i]] = func(data[i])
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    return scores


def for_db(data, df, func):
    ids = df.id.tolist()
    scores = pd.DataFrame(columns=["id", "score", "referred_id"])
    for i in range(0, len(data)):
        td = func(data[i])
        scores = scores.append(
            [pd.DataFrame({"id": [ids[i] for _ in range(len(df))], "score": td, "referred_id": ids})],
            ignore_index=True)
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
    return scores
