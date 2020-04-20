#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd

import sampler
import utils
from definitions import get_paths


def as_vertical():
    scores = utils.get_df(f, drop_nans=True)
    scores["quantiles"] = pd.qcut(scores["score"], 10, labels=False)
    scores.to_csv(SESSION + "score-quantiles.csv", index=False)


if __name__ == '__main__':
    ospaths = get_paths()
    SESSION = "Sesj2"
    SESSION = ospaths["datadir"] + SESSION + "/"
    f = SESSION + "mean-scores.csv"

    sf = SESSION + "new_plain.csv"
    # df = utils.get_df(sf, drop_nans=False, dt=True)
    as_vertical()
    q = pd.read_csv(SESSION + "score-quantiles.csv")

    sampler.sample_from_quantiles(data=q, n=2000, only_ids=True, sp=SESSION + "2000-quantile-sample.csv")
