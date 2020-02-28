#!/usr/bin/env python
"""
    Utilities used in the processing of the TWPC dataset, and for using the generated dataset afterwards
"""

import glob
import os

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


# Finds all files on a three level hierarchy of directories
def all_image_paths(basedir="E:/images/sorted/"):
    n_subdirs = np.arange(1, 45)
    subdirs = [basedir + str(x) + "/*" for x in n_subdirs]
    subsubdir = []
    for directory in subdirs:
        for file in glob.glob(directory):
            subsubdir.append(file)

    nested = [glob.glob(x + "/*") for x in subsubdir]  # Creates a list of files for each inner-most directory
    one_dim = [item for sublist in nested for item in sublist]  # Brings all files to one list
    return one_dim


def get_df(source, drop_nans=False, dt=True, category=None, article_type=None, drop_duplicates=False):
    df = pd.read_csv(source)
    print(f"Loaded {len(df)} articles.")
    if drop_nans is True:
        df = df.dropna()
        print(f"{len(df)} articles after dropping articles with NaNs")
    if drop_duplicates is True:
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
    if dt is True:
        def to_datetime(this_df):
            this_df['date'] = pd.to_datetime(this_df['date'])
            # this_df['date'] = this_df['date'].dt.date
            this_df['time'] = pd.to_datetime(this_df['time'])
            # this_df['time'] = this_df['time'].dt.time
            return this_df
            # try:
            #     this_df['time'] = pd.to_datetime(this_df['time'].apply(lambda x: x[x.rfind(" ") + 1:]),
            #                                      format="%H:%M:%S")
            #     return this_df
            # except (ValueError, TypeError):
            #     this_df['time'] = this_df['time'].apply(lambda x: datetime.strptime(x, "%H:%M:%S").time())
            #     return this_df
            # except AttributeError:
            #     print('Current DataFrame contains rows with invalid time values! '
            #           'Dropping these rows and attempting to convert again')
            #     this_df = this_df[this_df['time'].notna()]
            #     return to_datetime(this_df)

        df = to_datetime(df)
    return df


def get_pivot(p):
    df = pd.read_csv(p)
    table = df.pivot_table(index='id')
    return table


# returns: paths to images found by ids in df
# If from_Path is set to either drive or subdir, returns a 1D dict with id-path pairs for only the main images,
# else returns a ND dict with paths from sub directory and from drive.
def get_id_path_pairs(df, from_path=None, save_path=None, path="E:/images/sorted/"):
    allowable_path_args = ('drive', 'subdir')
    if from_path is not None and from_path not in allowable_path_args:
        raise ValueError(f"Bad argument {from_path}! Must be one of {allowable_path_args}")
    file_paths = all_image_paths(basedir=path)
    article_ids = df.id.tolist()
    id_paths = {}
    for file_path in file_paths:
        base_id = file_path[file_path.rfind("\\") + 1:file_path.rfind("-")]
        file_id = file_path[file_path.rfind("\\") + 1:file_path.rfind(".")]
        from_base = file_path[file_path.rfind("/") + 1:]
        if base_id in id_paths.keys():
            id_paths[base_id].update({  # Updates existing dictionary
                file_id: {
                    'drive': file_path,
                    'subdir': from_base
                }})
        else:
            id_paths[base_id] = {  # Creates a dictionary with id as key
                file_id: {
                    'drive': file_path,
                    'subdir': from_base
                }}

    filtered_id_path = {}
    if from_path is not None:
        n = 0
        for article_id in article_ids:
            try:
                p = id_paths[article_id][article_id + "-0"]
                filtered_id_path[article_id] = p[from_path]
            except KeyError:
                n += 1
        if n > 0:
            print(f"{n} articles have no main image! If passed DataFrame contains no NaNs, "
                  f"then the referred images are likely unavailable or corrupt, and were previously removed.")
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
