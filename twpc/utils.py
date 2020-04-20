#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Utilities used in the processing of the TWPC dataset, and for using the generated dataset afterwards
"""

import glob
import os
import sys

import pandas as pd
from bs4 import BeautifulSoup

import definitions


# last-index-of
def rindex(iterable, value):
    try:
        return len(iterable) - next(i for i, val in enumerate(reversed(iterable)) if val == value) - 1
    except StopIteration:
        raise ValueError


# Length of a file
def file_len(fname, encoding='utf-8'):
    empty_lines = 0
    with open(fname, 'r', encoding=encoding) as f:
        for i, line in enumerate(f):
            if line is None or line == '':
                empty_lines += 1
            pass
    return i + 1 - empty_lines


# Options menu when filepath exists
#
def options(path):
    alternatives = ('Overwrite', 'Generate new path (current path: ' + path + ')')
    for i, v in enumerate(alternatives):
        print(i, v)
    try:
        choice = int(input())
    except ValueError:
        print('Must be digit')
        return options(path)
    if choice == 0:
        return path
    if choice == 1:
        i = path.rfind('.')
        try:
            if int(path[i - 1]):
                new_no = int(path[i - 1]) + 1
                new_path = path[:i - 1] + str(new_no) + '.csv'
                path = new_path
        except ValueError:
            for n in range(2, 100):
                if os.path.exists(path[:i] + path[i:-4] + str(n) + '.csv'):
                    pass
                else:
                    path = path[:i] + path[i:-4] + str(n) + '.csv'
                    break
        return path


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def get_df(source, drop_nans=False, dt=False, category=None, article_type=None, drop_duplicates=False, has_image=False):
    df = pd.read_csv(source, sep=",")
    print(f"Loaded {len(df)} rows.")
    if drop_nans:
        df = df.dropna()
        print(f"{len(df)} items after dropping articles with NaNs")
    if drop_duplicates:
        print("Dropping duplicates by main text contents")
        df = df.drop_duplicates(subset='text')
        print(f"{len(df)} articles after dropping exact duplicates by main text")
    if article_type is not None:
        print(f"Locating articles of type {article_type}")
        df = df.loc[df.type == article_type]
        print(f"{len(df)} articles of type {article_type}")
    if category is not None:
        print(f"Locating articles within category {category}")
        df = df.loc[df.category == category]
        print(f"{len(df)} articles within category {category}")
    if has_image:
        print("Filtering out articles without a main image")
        file_paths = get_id_path_pairs(df, from_path="drive")
        df = df[df.id.isin(file_paths)]
        print(f"{len(df)} articles with a main image")
    if dt is True:
        def to_datetime(this_df):
            this_df['date'] = pd.to_datetime(this_df['date'])
            this_df['time'] = pd.to_datetime(this_df['time'])
            return this_df

        df = to_datetime(df)
    return df


def save_clean_copy(df, sp):
    if df['text'].str.contains("<br>").any():
        this_df_clean = df.copy()
        this_df_clean['image_caption'] = this_df_clean['image_caption'].apply(lambda x: rm_html(x))
        this_df_clean['text'] = this_df_clean['text'].apply(lambda x: rm_html(x))
        this_df_clean['author_bio'] = this_df_clean['author_bio'].apply(lambda x: rm_html(x))
        this_df_clean['category'] = this_df_clean['category'].apply(lambda x: rm_html(x))
        new_path = sp[:sp.rfind(".")] + "_plain" + ".csv"
        this_df_clean.to_csv(new_path, index=False)
        print(f"Saved {len(this_df_clean)} articles without HTML tags to {new_path}")
        return this_df_clean


def rm_html(text):
    return BeautifulSoup(text, "html.parser").text


def get_pivot(p, drop_self=True, as_compatible=False):
    df = pd.read_csv(p)
    ids = df.id.tolist()
    if drop_self:
        df = df.drop(columns=["id"])
        for i in range(len(ids)):
            df2 = df[df.columns[i]].drop(index=i)
            df[df.columns[i]] = df2
    df["id"] = ids
    if as_compatible:
        return df
    table = df.pivot_table(index='id')
    return table


# Finds all files on a three level hierarchy of directories
def all_image_paths(basedir=definitions.get_paths()["imagedir"]):
    return glob.glob(basedir + "*/*/*")


# returns: paths to images found by ids in df
# If from_Path is set to either drive or subdir, returns a 1D dict with id-path pairs for only the main images,
# else returns a ND dict with paths from sub directory and from drive.
def get_id_path_pairs(df, ignore_types=None, from_path=None, save_path=None):
    allowable_path_args = ('drive', 'subdir', 'self')
    if from_path is not None and from_path not in allowable_path_args:
        raise ValueError(f"Bad argument {from_path}! Must be one of {allowable_path_args}")
    file_paths = all_image_paths()
    article_ids = df.id.tolist()
    id_paths = {}
    for full_path in file_paths:
        full_path = full_path.replace("\\", "/").lower()
        base_id = full_path[full_path.rfind("/") + 1:full_path.rfind("-")]
        file_id = full_path[full_path.rfind("/") + 1:full_path.rfind(".")]
        from_parent = full_path[full_path.find("sorted/") + 6:]
        self = from_parent[from_parent.rfind("/"):]
        if base_id in id_paths.keys():
            id_paths[base_id].update({  # Updates existing dictionary
                file_id: {
                    'drive': full_path,
                    'subdir': from_parent,
                    'self': self,
                }})
        else:
            id_paths[base_id] = {  # Creates a dictionary with id as key
                file_id: {
                    'drive': full_path,
                    'subdir': from_parent,
                    'self': self,
                }}

    def not_of_type(f):
        if ignore_types is not None:
            return not f[from_path].lower().endswith(ignore_types)
        return True

    filtered_id_path = {}
    if from_path is not None:
        n = 0
        gif = 0
        for article_id in article_ids:
            try:
                p = id_paths[article_id][article_id + "-0"]
                if not_of_type(p):
                    filtered_id_path[article_id] = p[from_path]
                else:
                    gif += 1
            except KeyError:
                n += 1
        if n > 0:
            print(f"{n} articles have no main image! If passed DataFrame contains no NaNs, "
                  f"then the referred images are likely unavailable or corrupt, and were previously removed.")
        if gif > 0:
            print(f"{gif} articles' main image were of GIF format. These were ignored.")
        else:
            print("All articles in the passed DataFrame have a corresponding main image.")
    else:
        return filtered_id_path
    # Saving only works having passed a from_Path argument
    if save_path is not None and from_path is not None:
        pd.DataFrame({'id': list(filtered_id_path.keys()), 'path': list(filtered_id_path.values())}) \
            .to_csv(save_path)
        print(f"Saved {len(filtered_id_path)} id-path pairs to {save_path}")
    return filtered_id_path


def get_out_file(source_path):
    with open(source_path, mode="r") as file:
        content = file.readlines()
    embeddings = [x.split(",") for x in content]
    embedding_map = {}
    for entry in embeddings:
        embedding_map[entry[0]] = list(entry[1:])
    return pd.DataFrame({'id': list(embedding_map.keys()), 'embedding': list(embedding_map.values())})


def get_for_feature(p, feature):
    df = pd.read_csv(p)
    df = df.filter(["image", feature])
    df["id"] = df["image"].apply(lambda i: i[:i.find(".") - 2])
    return df


def create_article_files(df, dir_loc):
    for i in range(len(df)):
        df[i:i+1].to_csv(dir_loc + df[i:i+1].id.values[0] + ".csv", index=False)
        sys.stdout.write("\r" + f"{i + 1}/{len(df)}")
