#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script containing different ways to use Pillow's Verify

import concurrent.futures
import os
import threading
from multiprocessing import Pool

import numpy as np
from PIL import Image

from twpc.utils import all_image_paths


def verify_one(f):
    try:
        im = Image.open(f)
        im.verify()
        im.close()
        # print(f"OK: {f}")
    except (IOError, OSError, Image.DecompressionBombError):
        print(f"Fail: {f}")


# Verify image using multiprocessing
def mp_verify_images():
    p = Pool(processes=6)

    files = all_image_paths()

    print(f"Files to be checked: {len(files)}")

    result = p.map(verify_one, files)
    result = list(filter(None, result))
    print(f"Num corrupt files: {len(result)}")


# Thread class that verifies images given as paths in an iterable
class VerifyThread(threading.Thread):
    def __init__(self, file_chunk, worker_id):
        threading.Thread.__init__(self)
        self.file_chunk = file_chunk
        self.worker_id = worker_id

    def run(self):
        print(f"Starting worker {self.worker_id}")
        end = len(self.file_chunk)
        n_deleted = 0
        for index, img in enumerate(self.file_chunk):
            try:
                im = Image.open(img)
                im.verify()
                im.close()
            except (IOError, OSError, Image.DecompressionBombError, SyntaxError):
                print(f"{img} failed & removed: Worker {self.worker_id} on image {index}/{end}")
                os.remove(img)
                n_deleted += 1
                # print('Image {} could not be validated and will be removed'.format(file_name))
                # os.remove(image)
        return n_deleted


# Verify images using multithreading
def mt_verify_images():
    files = all_image_paths()
    n = 0
    threads = np.arange(1, 7, 1)
    thread_count = max(threads)
    chunk = len(files) // thread_count
    print(f"Starting {thread_count} workers")
    for i in threads:
        thread = VerifyThread(files[n:n + chunk], i)  # Each thread receives an equal # filepaths
        n += chunk
        thread.start()


# Singleprocessing
def verify_images():
    files = all_image_paths()
    for i, img in enumerate(files):
        try:
            im = Image.open(img)
            im.verify()
        except (IOError, OSError, Image.DecompressionBombError, SyntaxError):
            print(img)


# Alternative multithreading, by using ThreadPoolExecutor
def mt_verify_images_executor(workers=int):
    files = all_image_paths()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(verify_one, files)
