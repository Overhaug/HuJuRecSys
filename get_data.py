#!/usr/bin/env python
# A script to extract data from the Washington Post corpus, as well as images attached to the articles

import json
import os
import re
import sys
import time
from datetime import datetime as dt

import grequests
import json_lines as jl
import pandas as pd
import pytz
from PIL import Image

from bs4 import BeautifulSoup


def main(_max=None, batch_size=5000, path='../HuJuData/data/corpus/TWPC.jl'):
    articles = []
    num = 0
    with open(path, 'rb') as f:
        for article in jl.reader(f):
            article = convert_unix_to_datetime(article) if not False else convert_unix_to_datetime(article)
            article = add_image_url(article)
            if article['author'] is '' or article['author'] is None:
                article = get_author(article)
                article['subtype'] = 'compilation'
            else:
                article['subtype'] = 'standalone'
            if article is not None:
                articles.append(article)  # There are a handful of empty objects in the dataset
            else:
                continue
            if len(articles) == batch_size:
                num += batch_size
                get_as_csv(articles, path='../HuJuData/data/processed/corpus_csv.csv')
                articles = []
                if _max is not None:
                    print(num, 'of', _max)
                else:
                    print('Processed {} articles'.format(num))
                if _max is not None and _max - num in range(-25, 25):
                    return
        print('Processed {} articles'.format(num))
        get_as_csv(articles, path='../HuJuData/data/processed/corpus_csv.csv')
    f.close()
    return articles


def get_author(article):
    for k, v in article.items():
        if k == 'contents':
            for i in v:
                for key, content in i.items():
                    if str(content).__contains__('Compiled by'):
                        clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                        text = str(re.sub(clean, '', content))
                        i = str(text).find('by')
                        article['author'] = str(text)[i+3:]
                        return article


# Removes "type" property from object
def remove_type_from_object(item):
    del item['type']
    return item


# Adds image url from content array to root level
def add_image_url(item):
    url = get_singular_image_url(item)
    item['image_url'] = url
    return item


# Fetches image URL on the current article.
def get_singular_image_url(current_article):
    for content in current_article['contents']:
        if content is not None and content['type'] == 'image':
            return str(content['imageURL'])
    return 'null'


# Convert unix dates to datetime string
def convert_unix_to_datetime(item):
    try:
        item['published_date'] = dt.utcfromtimestamp(item['published_date'] / 1000.0) \
            .astimezone(pytz.timezone("America/New_York")) \
            .strftime('%Y-%m-%d')
    except TypeError:
        print('Unable to convert {} '.format(item['published_date']))
        return False
    except OSError:
        print('Invalid argument {}'.format(item['published_date']))  # Seemingly triggers only when published_date is 0
        return False
    return item


# Removes objects that correspond to a failed image request
def remove_failed_objects(failed, article_data):
    for item in article_data:
        url = get_image_url(item)
        if url in failed:
            article_data.remove(item)
            print("Removed object corresponding to failed request")
    return article_data


# Writes the data to a json file
# Modifies the file to be json serializable
def get_as_json(articles):
    articles = from_array_to_string(articles)
    with open('../HuJuData/data/processed/snippetTest2.json', 'w', encoding='utf-8') as file_handler:
        file_handler.write('[')
        for item in articles:
            file_handler.write(json.dumps(item, indent=2, ensure_ascii=False))
            if item != articles[-1]:
                file_handler.write(',')
        file_handler.write(']')

        print('Wrote to file {}'.format(file_handler.name))
        file_handler.close()


# returns a list of id-imageURL objects
def get_image_url(article):
    urls_list = []
    for index in range(len(article)):
        urls = {}
        num = 0
        for content in article[index]['contents']:
            if content is not None and content['type'] == 'image':
                urls['id'] = article[index]['id'] + '-' + str(num)
                urls['url'] = content['imageURL']
                urls_list.append(urls)
                num += 1
                urls = {}
    return urls_list


def extract_only_image_urls(path='../HuJuData/data/corpus/TWPC.jl', batch_size=20000):
    articles = []
    num = 0
    with open(path, 'rb') as file_reader:
        for article in jl.reader(file_reader):
            articles.append(article)
            if len(articles) == batch_size:
                get_as_csv(get_image_url(articles), path='../HuJuData/data/processed/image_urls.csv', convert=False)
                num += len(articles)
                print('{} processed ...'.format(num))
                articles = []
        get_as_csv(get_image_url(articles), path='../HuJuData/data/processed/image_urls.csv', convert=False)


# Writes data as csv
def get_as_csv(data, path, convert=True):
    if convert:
        processed_data = from_array_to_string(data)
        df = pd.DataFrame(processed_data)
    else:
        df = pd.DataFrame(data)

    if os.path.exists(path):
        df.to_csv(path, sep=',', index=False, header=False, mode='a')
    else:
        df.to_csv(path, sep=',', index=False, header=True, mode='w')


# Extract all content objects (in a json array) of type paragraph to a single string
def from_array_to_string(articles):
    content_array = []
    for article in articles:
        for key, value in article.items():
            if key == 'contents':
                for content in value:
                    if content is not None:
                        for cKey, cValue in content.items():
                            if cKey == 'subtype' and cValue == 'paragraph':
                                content_array.append(html_to_text(content['content']) + '<br><br>')
                                # plain_text = remove_urls_from_text(plain_text)
                del article[key]  # Deletes JSON array
                content_string = ' '.join(content_array).replace('\n', '')
                article['text'] = content_string  # Adds a new key-value, single string
                content_array = []
    return articles


def remove_urls_from_text(article):
    article = article.split()
    new_string = ''
    for word in range(len(article)):
        new_string += ' '
        x = re.sub(r'^https?:\/\/.*[\r\n]*', '', article[word], flags=re.MULTILINE)
        new_string += x
    return new_string


# Standard regex for cleaning html tags
def html_to_text(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.text
    # clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    # return str(re.sub(clean, '', text))


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
                print(n)
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
            # validate_image(img)
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


# Uses Pillow's Verify to check if an image is valid
def validate_image(image):
    file_name = image[image.rfind('/'):]
    try:
        if get_image_extension(image).upper() is '.PNG':
            im = Image.open(Image.composite(image, Image.new('RGB', image.size, 'white'), image))
        else:
            im = Image.open(image)
        im.verify()
    except (IOError, OSError):
        print('Image {} could not be validated and will be removed'.format(file_name))
        os.remove(image)


def log_failed_requests(id, url, status_code):
    if isinstance(id, list):
        entities = {
            'id': [],
            'url': [],
            'status_code': []
        }
        for x in range(len(id)):
            entities['id'].append(id[x])
            url_string = url[x] if str(url[x]).startswith('http') else 'nan'  # input nan for empty urls
            str(url_string).replace(',', '')  # Remove commas since we're using CSVs
            entities['url'].append(url_string)
            entities['status_code'].append(status_code[x])
        get_as_csv(data=entities, path='../HuJuData/data/logs/log_failed_requests.csv', convert=False)
    else:
        get_as_csv(data={'id': [id], 'url': [url], 'status_code': [status_code]},
                   path='../HuJuData/data/logs/log_failed_requests.csv', convert=False)


def exists_in_log(id):
    df = pd.read_csv('../HuJuData/data/logs/log_failed_requests.csv')
    count = 0
    for ids in df['id'].values:
        if ids is id:
            count += 1
    if count >= 1:
        return True
    return False


# Downloads images from a given list of urls
# Filenames equate to article ID
class ImageFetcher:
    def __init__(self, ids, url, incompleteURL=None, incompleteID=None):
        self.incompleteID = None
        self.incompleteURL = None
        self.status_codes = []
        if incompleteID is None:
            self.ids = [x for x in ids]
            self.urls = [x for x in url]
        else:
            self.ids = [x for x in incompleteID]
            self.urls = [x for x in incompleteURL]

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
                    print(
                        'Request at index {} failed more than 3 times with a client-side error or "No schema supplied".'
                            .format(self.ids[index]))
            elif request.status_code[0] is 5:
                print('Server error {}'.format(request.status_code))
                self.add_failed_requests(self.ids[index], self.urls[index], exception)
        else:
            self.add_failed_requests(self.ids[index], self.urls[index], exception)

    def get(self, limit=None):
        results = grequests.map((grequests.get(u) for u in self.urls),
                                exception_handler=self.exception,
                                size=limit,
                                stream=False,
                                gtimeout=240)
        failed = 0
        timestart = time.time()
        for x in range(len(self.urls)):
            if results[x] is not None:
                ext = get_image_extension(self.urls[x])
                path = 'E:/missing/' + self.ids[x] + '.' + set_image_extension(ext)
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
        timeend = time.time()
        print('Fetched and processed {} images, failed {}'.format(str(len(results) - failed), failed))
        print('Saving images took {:.3g}'.format(timeend - timestart))


def get_images(filepath='../HuJuData/data/processed/image_urls.csv', incomplete_urls=None,
               incomplete_ids=None, batch_size=50, _max=None, start_index=0, recursion_depth=0):
    def batch_instance(retry=False):
        remaining = _max - start_index if _max is not None else 656072 - start_index
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

    fetcher.get(limit=100)

    if fetcher.incompleteID is not None:
        if recursion_depth is not 1:
            print('Retrying failed requests ...')
            time.sleep(5)
            get_images(batch_size=batch_size, start_index=start_index, _max=_max,
                       incomplete_urls=fetcher.incompleteURL, incomplete_ids=fetcher.incompleteID,
                       recursion_depth=recursion_depth + 1)
        else:
            log_failed_requests(fetcher.incompleteID, fetcher.incompleteURL, fetcher.status_codes)
            print('Failed requests added to log and must be manually retried')
            for c1, c2 in zip(fetcher.incompleteID, fetcher.incompleteURL):
                print("%-9s %s" % (c1, c2))
            return
    else:
        print('No failed requests')


def image_fetcher(start_index=0, batch_size=50, _max=None):
    const_batch_size = batch_size
    const_start = start_index
    _max = int(const_start + _max) if _max is not None else _max
    start_of_process = time.time()
    total = 0
    while True:
        start_time = time.time()
        if start_index is _max:
            return False
        elif _max is None:
            get_images(batch_size=batch_size, start_index=start_index)
            start_index += const_batch_size
        else:
            get_images(batch_size=batch_size, start_index=start_index, _max=_max)
            start_index += const_batch_size
        end_time = time.time()
        total_time = end_time - start_of_process
        total += batch_size
        print('Processed {} in {:.3g} seconds'.format(batch_size, end_time - start_time))
        print('Progress: {} in ~{:.3g}'.format(total, int(total_time) / 60))
        print('---------------------------------------------------------------------')
        _max = _max - start_index if _max is not None else _max


if __name__ == '__main__':
    main(batch_size=100, _max=1000)
    # extract_only_image_urls(batch_size=50000)
    # image_fetcher(batch_size=1000, start_index=0)
    # move_files(source='../HuJuData/data/processed/images/', destination='E:/images/')
    # move_files(source='E:/images/', destination='F:/imgs/', copy=True)
    # resize_images()
