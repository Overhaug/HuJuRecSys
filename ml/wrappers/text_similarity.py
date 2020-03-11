#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common
import lda

FEATURE = "text"


def text_tfidf_cosine_sim(sp, df, db):
    vectors = common.tfidf(df, FEATURE)
    common.cosine_similarity(sp, df, vectors, db)


def text_textblob(sp, sp2, df, db, scoretype: tuple, update):
    if update:
        common.textblob_scores(sp, df, FEATURE, db, scoretype)
    common.compute_distance(sp, sp2, scoretype[1], db)


def text_lda(sp, df, db, session, update):
    lda.cs_lda(sp, df, FEATURE, db, session, update)
