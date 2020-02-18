#!/usr/bin/env python
# Utilities used in the processing of the TWPC dataset, and for using the generated dataset afterwards

import glob
import os
from datetime import datetime

import numpy as np
import pandas as pd


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
    alternatives = ('Overwrite', 'Generate new path (current path: '+path+')')
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
            if int(path[i-1]):
                new_no = int(path[i-1]) + 1
                new_path = path[:i-1] + str(new_no) + '.csv'
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
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


# Finds all files on a three level hierarchy of directories
def flattened_list_of_paths(basedir="E:/images/sorted/"):
    path = np.arange(1, 45)
    subdir = [basedir + str(x) + "/*" for x in path]
    per_dir = []
    for directory in subdir:
        for file in glob.glob(directory):
            per_dir.append(file)

    nested = [glob.glob(x + "/*") for x in per_dir]
    one_dim = [item for sublist in nested for item in sublist]

    return one_dim


def get_df(source, drop_nans, dt=True, topic=None):
    df = pd.read_csv(source)
    if drop_nans is True:
        df = df.dropna()
    if topic is not None:
        print(f"Locating all articles within category {topic}")
        df = df.loc[df.category == topic]
    if dt is True:
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        try:
            df['time'] = df['time'].apply(lambda x: datetime.strptime(x, "%H-%M-%S").time())
        except ValueError:
            df['time'] = pd.to_datetime(df['time'].apply(lambda x: x[x.rfind(" ")+1:]), format="%H:%M:%S")
    return df


# Only used after creating a sample from the main dataset. See sampler.py
# Takes a Dataframe as an argument, and uses each article's ID to find the appropriate (main) image.
def get_id_path_pairs(df, save_path=None, path="E:/images/sorted/"):
    file_paths = flattened_list_of_paths(basedir=path)
    article_ids = df.id.tolist()
    id_path = {}
    filtered_id_path = {}
    # Creates a dictionary (id_path) of all images available,
    # where key is an image's ID and value is the path to the image
    for file in file_paths:
        cfile = file[file.rfind("\\") + 1:file.rfind(".") - 2]
        if cfile in id_path.keys():
            id_path[cfile].append(file)
        else:
            id_path[cfile] = [file]

    # Results in a dict where key = relevant article ID, value = path to the relevant article ID
    for article_id in article_ids:
        try:
            for path in id_path[article_id]:
                if path[path.rfind("-") + 1:path.rfind("-") + 2] == "0":
                    filtered_id_path[article_id] = path
        except KeyError:
            pass
    if save_path is not None:
        pd.DataFrame({'id': list(filtered_id_path.keys()), 'path': list(filtered_id_path.values())})\
            .to_csv(save_path)
    return filtered_id_path
