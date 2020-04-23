#!/usr/bin/env python
"""
    A module that creates samples from TWPC
"""
import sys
from datetime import timedelta, date

import numpy as np
import pandas as pd

import utils
from utils import get_id_path_pairs

years = (2012, 2013, 2014, 2015, 2016, 2017)


def sample_frac_per_day(df, frac=10):
    def date_range(start, end):
        for n in range(int((end - start).days)):
            yield start + timedelta(n)

    min_date = pd.Timestamp(min(df['date']))
    max_date = pd.Timestamp(max(df['date']))

    start_date = date(min_date.year, min_date.month, min_date.day)
    end_date = date(max_date.year, max_date.month, max_date.day)

    new_df = pd.DataFrame()

    for a_date in date_range(start_date, end_date):
        articles_in_date = df.loc[df['date'] == pd.Timestamp(a_date)]
        try:
            sample = articles_in_date.sample(frac)
            new_df = pd.concat([new_df, sample])
        except ValueError:  # Number of items in article_in_date is less than sample size
            new_df = pd.concat([new_df, articles_in_date])

    save_as_csv(new_df, 'D:/newsRecSys/data/sample.csv')


def sample_stratified_per_year(df, sp, n):
    print(f"Sampling {n} articles per year in {years}")
    samples = pd.DataFrame()
    file_paths = get_id_path_pairs(df, from_path="drive")
    file_paths = list(file_paths.keys())
    for y in years:
        y_df = df.loc[df.date.dt.year == y]
        sys.stdout.write("\r" + f"Year {y}: {len(y_df)}")
        y_df = y_df[y_df.id.isin(file_paths)]
        sample = y_df.sample(n)
        samples = pd.concat([samples, sample])

    cols = df["id"]
    samples.drop(labels=["id"], axis=1, inplace=True)
    samples.insert(0, "id", cols)
    samples = samples.drop(["article_url", "type", "category", "subcategory", "subtype", "image_url"], axis=1)
    images = get_id_path_pairs(df, from_path="self")
    img = pd.DataFrame({'id': list(images.keys()), 'image': list(images.values())})
    samples["image"] = img["image"].where(img["id"] == df["id"])

    final_clean = utils.save_clean_copy(samples, sp)  # We save a clean copy here since it is unnecessary to store DT

    samples["date"] = samples["date"].apply(lambda t: t.date().strftime(format="%Y-%m-%d"))
    samples["time"] = samples["time"].apply(lambda t: t.time().strftime(format="%H:%M:%S"))
    samples["datetime"] = pd.to_datetime(samples["date"] + " " + samples["time"])
    save_as_csv(samples, sp)
    print(f"Saved {len(samples)} articles to {sp}")
    get_id_path_pairs(samples, save_path="E:/data/id_path.csv", from_path="drive")
    if final_clean is not None:
        return samples, final_clean
    else:
        return samples


def sample_from_quantiles(data, n: int, sep_scores: bool, sp: str):
    lower_quantile = data.loc[(data.quantiles == 0) & (data.score != np.nan)]
    lower_sample = lower_quantile.sample(n)

    middle_quantile = data.loc[(data.quantiles >= 1) & (data.quantiles <= 8) & (data.score != np.nan)]
    middle_sample = middle_quantile.sample(n)

    upper_quantile = data.loc[(data.quantiles == 9) & (data.score != np.nan)]
    upper_sample = upper_quantile.sample(n)

    merged_samples = pd.concat([lower_sample, middle_sample, upper_sample])
    # result = add_file_extension(merged_samples, ".csv")

    if sep_scores:
        sp2 = sp[:sp.rfind(".")] + "-with-scores.csv"
        merged_samples.to_csv(sp2, index=False, sep="\t")
        merged_samples.drop(["score", "quantiles"], axis=1, inplace=True)

    merged_samples.to_csv(sp, index=False, sep="\t")


def add_file_extension(data, extension):
    data["first"] = data["first"].apply(lambda i: i + extension)
    data["second"] = data["second"].apply(lambda i: i + extension)
    return data


def save_as_csv(df, path):
    df.to_csv(path, sep='\t', index=False, header=True, mode='w')


# sample_stratified_per_year(utils.get_df("D:/Progs/htdocs/news-study/data_new.csv", dt=True), "D:/Progs/htdocs/news-study/data_new.csv", 400)
