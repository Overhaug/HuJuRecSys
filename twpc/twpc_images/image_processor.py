#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script to download, verify and resize images from TREC Washington Post Corpus.

import os
import sys
import time

import grequests
import json_lines as jl
import pandas as pd
from PIL import Image

from utils import file_len


# Resize a set of images
def resize_images(file_dir=None, batch_size=10):
    files = []
    filenames = []

    file_types = ('JPEG', 'JPG', 'PNG', 'TIFF', 'TIF')
    d = 'E:/images/'
    new = 'E:/resized/'
    n = 0

    if file_dir is None:
        file_dir = os.listdir(d)
    for path in file_dir:
        full_path = os.path.join(d, path)
        if os.path.isfile(full_path) and str(full_path.upper()).endswith(file_types):
            files.append(full_path)
            filenames.append(path)
            n += 1
            if n == batch_size:
                break
    size = 400, 400
    for img in files:
        index = files.index(img)
        try:
            if get_image_extension(img).upper() is '.PNG':
                im = Image.open(Image.composite(img, Image.new('RGB', img.size, 'white'), img))
            else:
                im = Image.open(img)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(new + filenames[index], get_image_extension(filenames[index])[1:])
        except IOError:
            print('Could not resize {}'.format(img))
    resize_images(file_dir=[x for x in file_dir if x not in filenames])


def set_image_extension(ext):
    ext = ext.upper()
    if str(ext[1:]) == 'JPG' or str(ext[1:]) == 'JPEG':
        return 'JPEG'
    elif str(ext[1:]) == 'PNG':
        return 'PNG'
    elif str(ext[1:]) == 'TIF' or str(ext[1:]) == 'TIFF':
        return 'TIFF'
    else:
        return 'GIF'


def get_image_extension(string):
    str(string)
    i = string.rfind('.')
    return string[i:].upper()


def log_failed_requests(this_id, url, status_code):
    if isinstance(this_id, list):
        entities = {
            'id': [],
            'url': [],
            'status_code': []
        }
        for x in range(len(this_id)):
            entities['id'].append(this_id[x])
            url_string = url[x] if str(url[x]).startswith('http') else 'nan'
            str(url_string).replace(',', '')
            entities['url'].append(url_string)
            entities['status_code'].append(status_code[x])
        save_as_csv(data=entities, path='requests_log.csv')
    else:
        save_as_csv(data={'id': [this_id], 'url': [url], 'status_code': [status_code]},
                    path='requests_log.csv')


def exists_in_log(this_id):
    try:
        df = pd.read_csv('requests_log.csv')
    except OSError:
        return False
    count = 0
    for ids in df['id'].values:
        if ids == this_id:
            count += 1
    if count >= 1:
        return True
    return False


# Writes data as csv
def save_as_csv(data, path):
    df = pd.DataFrame(data)
    if os.path.exists(path):
        df.to_csv(path, sep=',', index=False, header=False, mode='a')
    else:
        df.to_csv(path, sep=',', index=False, header=True, mode='w')


# Downloads images from a given list of urls
# Filenames equate to article ID + enumerated suffix
class ImageFetcher:
    def __init__(self, ids, url, incomplete_urls=None, incomplete_ids=None):
        self.incompleteID = None
        self.incompleteURL = None
        self.status_codes = []
        if incomplete_ids is None:
            self.ids = [x for x in ids]
            self.urls = [x for x in url]
        else:
            self.ids = [x for x in incomplete_ids]
            self.urls = [x for x in incomplete_urls]

    def add_failed_requests(self, ids, urls, exception):
        if self.incompleteID is None:
            self.incompleteID = [ids]
            self.incompleteURL = [urls]
            self.status_codes.append(exception)
        else:
            self.incompleteID.append(ids)
            self.incompleteURL.append(urls)
            self.status_codes.append(exception)

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))
        index = self.urls.index(request.url)
        if str(exception).__contains__('No schema supplied'):
            if not exists_in_log(self.ids[index]):
                self.add_failed_requests(self.ids[index], None, exception)
            else:
                self.add_failed_requests(self.ids[index], None, exception)
        elif hasattr(request, 'status_code'):
            if request.statuscode[0] is 4:
                print(request.status_code)
                if not exists_in_log(self.ids[index]):
                    self.add_failed_requests(self.ids[index], self.urls[index], exception)
                else:
                    print('Request at index {} failed more than 3 times '
                          'with a client-side error or "No schema supplied".'.format(self.ids[index]))
            elif request.status_code[0] is 5:
                print('Server error {}'.format(request.status_code))
                self.add_failed_requests(self.ids[index], self.urls[index], exception)
        else:
            self.add_failed_requests(self.ids[index], self.urls[index], exception)

    def get(self, save_loc, limit=None):
        results = grequests.map((grequests.get(u) for u in self.urls),
                                exception_handler=self.exception,
                                size=limit,
                                stream=False,
                                gtimeout=240)
        failed = 0
        for x in range(len(self.urls)):
            if results[x] is not None:
                ext = get_image_extension(self.urls[x])
                path = save_loc + self.ids[x] + '.' + set_image_extension(ext)
                with open(path, 'wb') as handler:
                    handler.write(results[x].content)
                    sys.stdout.write('\r' + 'Saved {} images ... '.format(str(x + 1 - failed)))
                results[x].close()
            else:
                try:
                    if self.ids[x] not in self.incompleteID:
                        self.add_failed_requests(self.ids[x], self.urls[x], 'Gevent joinall timeout')
                except TypeError:
                    self.add_failed_requests(self.ids[x], self.urls[x], 'Gevent joinall timeout')
                failed += 1
        print('Fetched and processed {} images, failed {}'.format(str(len(results) - failed), failed))


def get_images(filepath, incomplete_urls=None,
               incomplete_ids=None, batch_size=50, _max=None, start_index=0, recursion_depth=0, save_loc=os.curdir):
    def batch_instance(retry=False):
        remaining = _max - start_index
        if filepath is not None and retry is False:
            with open(filepath, 'r', encoding='utf-8') as file_handler:
                df = pd.read_csv(file_handler)
                print('Fetching images from index {} to {} of {}'.format(start_index, start_index + batch_size,
                                                                         remaining))
                try:
                    image_fetch = ImageFetcher(df['id'][start_index:start_index + batch_size],
                                               df['url'][start_index:start_index + batch_size])
                except IndexError:
                    image_fetch = ImageFetcher(df['id'][start_index:656072],
                                               df['url'][start_index:656072])
                return image_fetch
        if filepath is not None and retry is True:
            image_fetch = ImageFetcher(incomplete_ids, incomplete_urls)
            return image_fetch

    if incomplete_urls is None:
        fetcher = batch_instance()
    else:
        fetcher = batch_instance(retry=True)

    fetcher.get(limit=100, save_loc=save_loc)

    if fetcher.incompleteID is not None:
        if recursion_depth is not 1:
            print('Retrying failed requests ...')
            time.sleep(5)
            get_images(batch_size=batch_size, start_index=start_index, _max=_max,
                       incomplete_urls=fetcher.incompleteURL, incomplete_ids=fetcher.incompleteID,
                       recursion_depth=recursion_depth + 1, save_loc=save_loc, filepath=filepath)
        else:
            log_failed_requests(fetcher.incompleteID, fetcher.incompleteURL, fetcher.status_codes)
            print('Failed requests added to log and must be manually retried')
            for c1, c2 in zip(fetcher.incompleteID, fetcher.incompleteURL):
                print("%-9s %s" % (c1, c2))
            return
    else:
        print('No failed requests')


def image_fetcher(source, save_loc=os.curdir, start_index=0, batch_size=50, _max=None, max_retries=1):
    const_start = start_index
    _max = int(const_start + _max) if _max is not None else file_len(source)
    start_of_process = time.time()
    total = 0
    while True:
        start_time = time.time()
        if start_index == _max:
            return
        elif _max is None:
            get_images(filepath=source, save_loc=save_loc, batch_size=batch_size, start_index=start_index,
                       recursion_depth=max_retries)
            start_index += batch_size
        else:
            get_images(filepath=source, save_loc=save_loc, batch_size=batch_size, start_index=start_index,
                       _max=_max, recursion_depth=max_retries)
            start_index += batch_size
        end_time = time.time()
        total_time = end_time - start_of_process
        total += batch_size
        print('Processed {} in {:.3g} seconds'.format(batch_size, end_time - start_time))
        print('Progress: {} in ~{:.3g}'.format(total, int(total_time) / 60))
        print('---------------------------------------------------------------------')


# returns a list of id-imageURL objects
def get_image_url(articles):
    urls_list = []
    for index in range(len(articles)):
        urls = {}
        num = 0
        for content in articles[index]['contents']:
            if content is not None and content['type'] == 'image':
                urls['id'] = articles[index]['id'] + '-' + str(num)
                urls['url'] = content['imageURL']
                urls_list.append(urls)
                num += 1
                urls = {}
    return urls_list


def extract_image_urls(source, save_loc='image_urls.csv', batch_size=20000):
    articles = []
    num = 0
    _max = file_len(source)
    print(_max)
    with open(source, 'rb') as file_reader:
        for article in jl.reader(file_reader):
            articles.append(article)
            num += 1
            if num % batch_size == 0:
                save_as_csv(get_image_url(articles), path=save_loc)
                print('Processed {} of {}'.format(num, _max))
                articles = []
            if num == _max:
                print('Processed {} of {}'.format(num, _max))
                print('Finished extracting URLs')
                save_as_csv(get_image_url(articles), path=save_loc)


if __name__ == '__main__':
    # image_fetcher(batch_size=10, start_index=10, max_retries=1,
    #              source='../HuJuData/data/processed/image_urls.csv',
    #              save_loc='../HuJuData/data/processed/images/')

    extract_image_urls(source='../HuJuData/data/corpus/TWPC.jl', batch_size=200000)
