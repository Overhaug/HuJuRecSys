#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common

FEATURE = "author_bio"


def bio_tfidf_cosine_sim(sp, df, db):
    vectors = common.tfidf(df, FEATURE)
    common.cosine_similarity(sp, df, vectors, db)


def bio_levenshtein(sp, df, db):
    common.levenshtein(sp, df, FEATURE, db)


def bio_jaccard(sp, df, db):
    common.jaccard(sp, df, FEATURE, db)
