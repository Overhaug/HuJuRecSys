#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd

import sampler
import utils

SESSION = ""


def as_vertical(sf):
    # We drop NAN because each 2400 subset (1 article) contains 1 nan (a reference to itself)
    # This means we ends up with 2400 fewer rows
    scores = utils.get_df(sf, drop_nans=True)
    scores["quantiles"] = pd.qcut(scores["score"], 10, labels=False)
    scores.to_csv(SESSION + "score-quantiles.csv", index=False)


def run(session_name):
    print("Creating 10 quantiles")
    global SESSION
    SESSION = session_name
    f = SESSION + "mean-scores.csv"
    as_vertical(f)

    q = pd.read_csv(SESSION + "score-quantiles.csv")
    sampler.sample_from_quantiles(data=q, n=2000, sep_scores=True, sp=SESSION + "pairs_2000-quantile-sample.csv")
