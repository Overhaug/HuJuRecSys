#!/usr/bin/env python

import glob
import os
from random import shuffle

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
        for i, l in enumerate(f):
            if l == '' or l is None:
                empty_lines += 1
            pass
    return i + 1 - empty_lines


# Options menu when filepath exists
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


# A non-generic function to get a onedimensional list of paths, containing full paths to every image
def onedim_list_of_paths():
    basedir = "E:/images/sorted/"
    path = np.arange(1, 45)
    subdir = [basedir + str(x) + "/*" for x in path]
    per_dir = []
    for directory in subdir:
        for file in glob.glob(directory):
            per_dir.append(file)

    nested = [glob.glob(x + "/*") for x in per_dir]
    one_dim = [item for sublist in nested for item in sublist]

    return one_dim


def get_df(source, only_dates=False, drop_nans=True, dt=True, topic=None):
    df = pd.read_csv(source)
    if topic is not None:
        df = df.loc[df.category == topic]
    if only_dates is True:
        return pd.DataFrame(
            {'date': pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')})
    if dt is True:
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        df['time'] = pd.to_datetime(df['time'], format='%H-%M-%S', errors='coerce')
    if drop_nans is True:
        df.dropna(inplace=True)
    return df