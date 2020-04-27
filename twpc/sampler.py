#!/usr/bin/env python
"""
    A module that creates samples from TWPC
"""
from datetime import timedelta, date

import numpy as np
import pandas as pd
from PIL import Image, ImageFile

import utils
from utils import get_id_path_pairs

ImageFile.LOAD_TRUNCATED_IMAGES = True

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


def is_placeholder(i):
    im = Image.open(i)
    return im.height == 100 and im.width == 145


def sample_n_per_year(df, sp, n):
    """
    Samples n articles per year as defined by variable years.
    Makes sure no articles sampled have a main image believed to be a placeholder image.
    Ensures that all articles have a main image, and never of type .GIF
    Finds and adds the filename of each image to each article
    :param df: pandas DataFrame to sample from
    :param sp: save path
    :param n: how many articles per year
    :return: a clean version of the resulting sample dataset
    """
    print(f"Sampling {n} articles per year in {years}")
    file_paths = get_id_path_pairs(df, from_path="drive", ignore_types="gif")
    file_path_ids = list(file_paths.keys())

    def sample_ignore_placeholders(source, result, x, recurse=False):
        """
        A function to sample x number of samples while ignoring articles with placeholder images.
        If a sample-set contains articles with placeholder images, a subset of the results is carried
        over to a new iteration of the function through recursion,
        and finds the remaining x articles needed to reach initial x.
        :param source: DF to sample from
        :param result: Resulting DF without samples containing placeholders
        :param x: The current number of articles to sample
        :param recurse: Whether this iteration of the function is a product of recursion
        :return: Initial x number of samples
        """
        source = source.reset_index(level=0, drop=True)
        this_sample = source.sample(x)
        source = source.drop(this_sample.index.values.tolist())  # .reset_index()
        this_sample = this_sample.reset_index(level=0, drop=True)

        placeholders = []
        for i in this_sample.id:
            if is_placeholder(file_paths[i]):
                placeholders.append(this_sample.index[this_sample.id == i].tolist()[0])
        if len(this_sample) - len(placeholders) == x or len(placeholders) == 0:
            if recurse:
                return pd.concat([this_sample, result])
            return this_sample
        else:
            print(f"{len(placeholders)} articles had a placeholder image. Finding replacements ...")
            this_sample = this_sample.drop(this_sample.index[placeholders])
            this_sample = pd.concat([result, this_sample])
            return sample_ignore_placeholders(source, this_sample, len(placeholders), True)

    samples = pd.DataFrame()
    for y in years:
        y_df = df.loc[df.date.dt.year == y]
        print(f"Year {y}: {len(y_df)}")
        y_df = y_df[y_df.id.isin(file_path_ids)]
        sample = sample_ignore_placeholders(y_df, None, n)
        samples = pd.concat([samples, sample])

    # Finds "self"-path for each image, i.e. from the image's directory
    samples = samples.reset_index()
    images = get_id_path_pairs(samples, from_path="self")
    img = pd.DataFrame({'id': list(images.keys()), 'image': list(images.values())})
    samples["image"] = img["image"].where(img["id"] == samples["id"])

    # Simply to place the id column at colindex 0
    cols = samples["id"]
    samples.drop(labels=["id"], axis=1, inplace=True)
    samples.insert(0, "id", cols)

    # Cols not needed for neither calculations nor survey
    cols_to_drop = ["article_url", "type", "category", "subtype", "image_url", "index"]
    samples = samples.drop(cols_to_drop, axis=1)

    # Concatenate date and time to a single datetime for easier viewing on survey
    samples["date"] = samples["date"].apply(lambda t: t.date().strftime(format="%Y-%m-%d"))
    samples["time"] = samples["time"].apply(lambda t: t.time().strftime(format="%H:%M:%S"))
    samples["datetime"] = pd.to_datetime(samples["date"] + " " + samples["time"])

    # Rearrange cols (hard-coded order)
    samples = rearrange_cols(samples)

    final_clean = utils.save_clean_copy(samples, sp)
    samples.to_csv(sp, index=False, header=True, sep="\t")
    print(f"Saved {len(samples)} articles to {sp}")

    # Store a csv file with ID and path to image for each article
    get_id_path_pairs(samples, save_path=sp[:sp.rfind("/")] + "/id_path.csv", from_path="drive")
    return final_clean


def sample_from_quantiles(data, n: int, sep_scores: bool, sp: str):
    print(f"Sampling from quantiles, {n} per range")
    lower_quantile = data.loc[(data.quantiles == 0) & (data.score != np.nan)]
    lower_sample = lower_quantile.sample(n)

    middle_quantile = data.loc[(data.quantiles >= 1) & (data.quantiles <= 8) & (data.score != np.nan)]
    middle_sample = middle_quantile.sample(n)

    upper_quantile = data.loc[(data.quantiles == 9) & (data.score != np.nan)]
    upper_sample = upper_quantile.sample(n)

    merged_samples = pd.concat([lower_sample, middle_sample, upper_sample])

    if sep_scores:
        sp2 = sp[:sp.rfind(".")] + "-with-scores.csv"
        merged_samples.to_csv(sp2, index=False, sep="\t")
        merged_samples.drop(["score", "quantiles"], axis=1, inplace=True)

    merged_samples.to_csv(sp, index=False, sep="\t")


def rearrange_cols(df):
    cols = ["id", "subcategory", "title", "image", "image_caption",
            "author", "date", "time", "datetime", "text", "author_bio"]
    return df[cols]


def add_file_extension(data, extension):
    data["first"] = data["first"].apply(lambda i: i + extension)
    data["second"] = data["second"].apply(lambda i: i + extension)
    return data


def save_as_csv(df, path):
    df.to_csv(path, sep='\t', index=False, header=True, mode='w')
