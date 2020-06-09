#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common
import lda

FEATURE = "author_bio"


def bio_tfidf_cosine_sim(sp, df):
    vectors = common.tfidf(df, FEATURE)
    common.cosine_similarity(sp, df, vectors)


def bio_levenshtein(sp, df):
    common.levenshtein(sp, df, FEATURE)


def bio_jaccard(sp, df):
    common.jaccard(sp, df, FEATURE)


def bio_lda(sp, df, session, update_model):
    lda.cs_lda(sp, df, FEATURE, session, update_model)
