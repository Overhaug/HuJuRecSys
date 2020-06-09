#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common

FEATURE = "author"


def author_jaccard(sp, df):
    common.jaccard(sp, df, FEATURE)
