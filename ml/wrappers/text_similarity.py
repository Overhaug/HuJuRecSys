#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common
import lda

FEATURE = "text"


def text_tfidf_cosine_sim(sp, df):
    vectors = common.tfidf(df, FEATURE)
    common.cosine_similarity(sp, df, vectors)


def text_tfidf_cosine_sim_length_constrained(sp, df, n):
    df[FEATURE] = common.constrain_length(df, FEATURE, n)
    vectors = common.tfidf(df, FEATURE)
    common.cosine_similarity(sp, df, vectors)


def text_textblob(sp, sp2, df, scoretype: tuple, update):
    if update:
        common.textblob_scores(sp, df, FEATURE, scoretype)
    common.compute_distance(sp, sp2, scoretype[1], False)


def text_lda(sp, df, session, update):
    lda.cs_lda(sp, df, FEATURE, session, update)
