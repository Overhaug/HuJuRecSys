#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Preprocesses (moves and resizes) images relevant to a sample dataset.
"""

import glob
import os
import threading

import numpy as np
from PIL import Image, ImageFile

import utils

ImageFile.LOAD_TRUNCATED_IMAGES = True

SESSION = ""
IMAGE_SESSION = ""


class ResizeThread(threading.Thread):
    def __init__(self, file_chunk, worker_id, target_size):
        threading.Thread.__init__(self)
        self.file_chunk = file_chunk
        self.worker_id = worker_id
        self.target_size = target_size

    def run(self):
        print(f"Starting worker {self.worker_id}")
        for index, img in enumerate(self.file_chunk):
            im = Image.open(img)
            im.thumbnail(self.target_size, Image.ANTIALIAS)
            name = img[img.rfind("/") + 1:]
            im.save(IMAGE_SESSION + name, im.format)
        print(f"Worker {self.worker_id} finished its batch.")


def copy_and_resize_sample_images(files, target_size):
    n = 0
    threads = np.arange(1, 7, 1)
    thread_count = max(threads)
    chunk = len(files) // thread_count
    print(f"Starting {thread_count} workers")
    workers = []
    for i in threads:
        thread = ResizeThread(files[n:n + chunk], i, target_size)  # Each thread receives an equal # filepaths
        n += chunk
        workers.append(thread)
        thread.start()

    for w in workers:
        w.join()


def create_image_paths(df_path, cat):
    df = utils.get_df(df_path, category=cat, drop_nans=True, drop_duplicates=True)
    file_paths = utils.get_id_path_pairs(df, from_path="drive", ignore_types="gif")
    file_paths = list(file_paths.keys())
    df = df[df.id.isin(file_paths)]

    df.to_csv(SESSION + "politics.csv", index=False)
    utils.save_clean_copy(df, SESSION + "politics.csv")
    utils.get_id_path_pairs(df, save_path=SESSION + "id_path_all.csv", from_path="drive")


def remove_images_in_session():
    files = glob.glob(IMAGE_SESSION + "*")
    for i in files:
        os.remove(i)


def run(session_name, target_size):
    print(f"Starting preprocessing of images for session {session_name}")
    global SESSION, IMAGE_SESSION
    SESSION = session_name
    IMAGE_SESSION = SESSION + "resized_images/"
    if not os.path.exists(IMAGE_SESSION):
        os.mkdir(IMAGE_SESSION)
        print(f"New directory: {IMAGE_SESSION}")

    f = utils.get_df(SESSION + "id_path.csv")
    f = f.path.values.tolist()
    copy_and_resize_sample_images(f, target_size)
