#!/usr/bin/env python
"""
    A module that creates samples from TWPC
"""
import os
import sys
from datetime import timedelta, date, datetime

import pandas as pd
from bs4 import BeautifulSoup

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
    timestamp = datetime.now()
    ts_string = timestamp.strftime("%d-%m-%Y-%H-%M")
    sp = sp + ts_string
    session = sp[:sp.rfind("/")]
    if os.path.exists(session):
        raise OSError(f"Session {session} exists")
    os.mkdir(session)
    print(f"Sampling {n} articles per year in {years}'")
    final = pd.DataFrame()
    file_paths = get_id_path_pairs(df, from_path="drive")
    file_paths = list(file_paths.keys())
    for y in years:
        y_df = df.loc[df.date.dt.year == y]
        sys.stdout.write("\r" + f"Year {y}: {len(y_df)}")
        y_df = y_df[y_df.id.isin(file_paths)]
        sample = y_df.sample(n)
        final = pd.concat([final, sample])

    save_as_csv(final, sp)
    print(f"Saved {len(final)} articles to {sp}")

    def clean_current_sample(this_df):
        if this_df['text'].str.contains("<br>").any():
            this_df_clean = this_df.copy()
            this_df_clean['image_caption'] = this_df_clean['image_caption'].apply(lambda x: rm_html(x))
            this_df_clean['text'] = this_df_clean['text'].apply(lambda x: rm_html(x))
            this_df_clean['author_bio'] = this_df_clean['author_bio'].apply(lambda x: rm_html(x))
            this_df_clean['category'] = this_df_clean['category'].apply(lambda x: rm_html(x))
            new_path = sp[:sp.rfind(".")] + "_plain" + ".csv"
            save_as_csv(this_df_clean, new_path)
            print(f"Saved {len(this_df_clean)} articles without HTML tags to {new_path}")
            return this_df_clean

    final_clean = clean_current_sample(this_df=final)
    get_id_path_pairs(final, save_path="E:/data/id_path.csv", from_path="drive")
    if final_clean is not None:
        return final, final_clean
    else:
        return final


def save_as_csv(df, path):
    df.to_csv(path, sep=',', index=False, header=True, mode='w')


def rm_html(text):
    return BeautifulSoup(text, "html.parser").text
