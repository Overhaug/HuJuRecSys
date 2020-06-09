#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common

FEATURE = "subcategory"


def subcategory_jacc(sp, df):
    common.jaccard(sp, df, FEATURE)
