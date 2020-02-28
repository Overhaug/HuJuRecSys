#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Script containing different ways to use Pillow's Verify
"""

import concurrent.futures
import os
import threading

import numpy as np
from PIL import Image

from twpc.utils import all_image_paths


def verify_one(file):
    try:
        im = Image.open(file)
        im.verify()
        im.close()
        # print(f"OK: {f}")
    except (IOError, OSError, Image.DecompressionBombError):
        print(f"Fail: {file}")


# Verify image using multiprocessing
def mp_verify_images():
    from multiprocessing import Pool
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
                try:
                    os.remove(img)
                    print(f"W:{self.worker_id} {index}/{end}: {img} could not be verified and was removed.")
                    n_deleted += 1
                except PermissionError:
                    print(f"PermissionError: W:{self.worker_id} {index}/{end}: {img} "
                          f"The file is likely already deleted.")
            except PermissionError:
                print(f"PermissionError: The file is likely already deleted.")
        print(f"Worker {self.worker_id} detected and deleted {n_deleted} unverifiable images.")


# Verify images using multithreading
def mt_verify_images(files):
    n = 0
    threads = np.arange(1, 7, 1)
    thread_count = max(threads)
    chunk = len(files) // thread_count
    print(f"Starting {thread_count} workers")
    for i in threads:
        thread = VerifyThread(files[n:n + chunk], i)  # Each thread receives an equal # filepaths
        n += chunk
        thread.start()


def check_validity_of_paths(paths):
    print("Checking validity of paths")
    paths = [file_exists(f) for f in paths]
    filtered_paths = list(filter(None.__ne__, paths))
    n_not_a_path = len(paths) - len(filtered_paths)
    if n_not_a_path != 0:
        raise OSError(f"{n_not_a_path} paths could not be verified!")


def file_exists(f):
    if os.path.exists(f):
        return f
    return None


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
def mt_verify_images_executor(workers):
    files = all_image_paths()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(verify_one, files)
