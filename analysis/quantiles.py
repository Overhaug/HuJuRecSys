#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd

import sampler
import utils
from definitions import get_paths


def as_vertical():
    scores = utils.get_df(f, drop_nans=True)
    # ids = scores.id.tolist()

    # q1_data = pd.DataFrame()
    # q2_data = pd.DataFrame()
    # q3_data = pd.DataFrame()

    # For each article ID, find the ID of each article that matches the score criteria
    # for j, i in enumerate(ids):
    #     refs = scores[i].loc[scores[i] <= 0.1].index.values.tolist()
    #     d = pd.DataFrame({
    #         "first": [i for _ in range(len(refs))],
    #         "second": map(ids.__getitem__, refs)
    #     })
    #     q1_data = pd.concat([q1_data, d])
    #
    #     refs = scores[i].loc[(scores[i] > 0.1) & (scores[i] < 0.9)].index.values.tolist()
    #     d = pd.DataFrame({
    #         "first": [i for _ in range(len(refs))],
    #         "second": map(ids.__getitem__, refs)
    #     })
    #     q2_data = pd.concat([q2_data, d])
    #
    #     refs = scores[i].loc[scores[i] >= 0.9].index.values.tolist()
    #     d = pd.DataFrame({
    #         "first": [i for _ in range(len(refs))],
    #         "second": map(ids.__getitem__, refs)
    #     })
    #     q3_data = pd.concat([q3_data, d])

    scores["quantiles"] = pd.qcut(scores["score"], 10, labels=False)

    scores.to_csv(SESSION + "score-quantiles.csv", index=False)

    # q1_data.to_csv(SESSION + "q1.csv", index=False)
    # q2_data.to_csv(SESSION + "q2.csv", index=False)
    # q3_data.to_csv(SESSION + "q3.csv", index=False)


def as_pivot():
    scores = utils.get_pivot(f, as_compatible=True)
    ids = scores.id.tolist()

    q1_data = pd.DataFrame()
    q2_data = pd.DataFrame()
    q3_data = pd.DataFrame()
    for j, i in enumerate(ids):
        q1_data[i] = scores[i].loc[scores[i] <= 0.1].index.values.tolist()

        q2_data[i] = scores[i].loc[(scores[i] > 0.1) & (scores[i] < 0.9)].index.values.tolist()

        q3_data[i] = scores[i].loc[scores[i] >= 0.9].index.values.tolist()

    q1 = pd.DataFrame(columns=ids)
    q1["id"] = ids

    q2 = pd.DataFrame(columns=ids)
    q2["id"] = ids

    q3 = pd.DataFrame(columns=ids)
    q3["id"] = ids

    for k, v in q1_data.items():
        q1[k] = df.iloc[v].id

    for k, v in q2_data.items():
        q2[k] = df.iloc[v].id

    for k, v in q3_data.items():
        q3[k] = df.iloc[v].id


if __name__ == '__main__':
    ospaths = get_paths()
    SESSION = "Sesj2"
    SESSION = ospaths["datadir"] + SESSION + "/"
    f = SESSION + "mean-scores.csv"

    sf = SESSION + "new_plain.csv"
    df = utils.get_df(sf, drop_nans=False, dt=True)
    as_vertical()
    # q1 = pd.read_csv(SESSION + "q1.csv")
    # q2 = pd.read_csv(SESSION + "q2.csv")
    # q3 = pd.read_csv(SESSION + "q3.csv")
    q = pd.read_csv(SESSION + "score-quantiles.csv")

    sampler.sample_from_quantiles(data=q, n=2000, only_ids=True, sp=SESSION + "2000-quantile-sample.csv")
