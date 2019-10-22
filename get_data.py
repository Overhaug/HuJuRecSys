#!/usr/bin/env python
# A script to extract data from the Washington Post corpus, as well as images attached to the articles

import json
import os
import re
import time
from datetime import datetime as dt

import grequests
import json_lines as jl
import pandas as pd
import pytz
from PIL import Image


def main(_max=None, batch_size=5000, path='../HuJuData/data/corpus/TREC_Washington_Post_collection.v2.jl'):
    articles = []
    num = 0
    with open(path, 'rb') as f:
        for article in jl.reader(f):
            article = convert_unix_to_datetime(article) if not False else convert_unix_to_datetime(article)
            article = add_image_url(article)
            article = remove_type_from_object(article)
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
    content_string = ' '
    for article in articles:
        for key, value in article.items():
            if key == 'contents':
                for content in value:
                    if content is not None:
                        for cKey, cValue in content.items():
                            if cKey == 'subtype' and cValue == 'paragraph':
                                plain_text = html_to_text(content['content'])
                                plain_text = remove_urls_from_text(plain_text)
                                content_string += plain_text
                article.pop(key)  # Deletes JSON array
                article['text'] = content_string  # Adds a new key-value, simple plain text
                content_string = ' '
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
    clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    return str(re.sub(clean, '', text))


# Resize a set of images
def resize_images(ids):
    files = []
    filenames = []

    file_types = ('JPG', 'PNG', 'TIF')
    d = '../HuJuData/data/processed/images/'
    for path in os.listdir(d):
        full_path = os.path.join(d, path)
        if os.path.isfile(full_path) and path.split('.')[0] in ids and str(full_path.upper()).endswith(file_types):
            files.append(full_path)
            filenames.append(path)

    size = 400, 400
    for img in files:
        index = files.index(img)
        try:
            print(get_image_extension(img).upper())
            if get_image_extension(img).upper() is '.PNG':
                im = Image.open(Image.composite(img, Image.new('RGB', img.size, 'white'), img))
            else:
                im = Image.open(img)
            # im = Image.open(img)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(d + filenames[index], set_image_extension(get_image_extension(img)))
        except IOError:
            print('Could not resize {}'.format(img))
        validate_image(files[index])


def get_image_extension(string):
    str(string)
    i = string.rfind('.')
    return string[i:]


def set_image_extension(ext):
    ext = ext.upper()
    if ext is 'JPG' or 'JPEG': return 'JPEG'
    if ext is 'PNG': return 'PNG'
    if ext is 'TIF' or 'TIFF': return 'TIFF'
    if ext is 'GIF': return 'GIF'


# If the image can be opened, assume it is a valid file
def validate_image(image):
    try:
        Image.open(image)
    except OSError:
        file_name = image[image.rfind('/'):]
        print(get_image_extension(file_name[file_name.find('.'):]))
        if get_image_extension(file_name[file_name.find('.'):]).upper() is '.PNG':
            try:
                Image.open(Image.composite(image, Image.new('RGB', image.size, 'white'), image))
            except OSError:
                print('Image {} could not be validated and will be removed'.format(file_name))
                os.remove(image)


# Downloads images from a given list of urls
# Filenames equate to article ID
class ImageFetcher:
    def __init__(self, ids, url, incompleteURL=None, incompleteID=None):
        self.incompleteID = None
        self.incompleteURL = None
        if incompleteID is None:
            self.ids = [x for x in ids]
            self.urls = [x for x in url]
        else:
            self.ids = [x for x in incompleteID]
            self.urls = [x for x in incompleteURL]

    def add_failed_requests(self, id, url):
        if self.incompleteID is None:
            self.incompleteID = list().append(id)
            self.incompleteURL = list().append(url)
        else:
            self.incompleteID.append(id)
            self.incompleteURL.append(url)

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))
        self.add_failed_requests(self.urls.index(request.url), request.url)

    def get(self, limit=None):
        results = grequests.map((grequests.get(u) for u in self.urls),
                                exception_handler=self.exception,
                                size=limit,
                                stream=False)
        for x in range(len(self.urls)):
            if results[x] is not None:
                path = '../HuJuData/data/processed/images/' + self.ids[x] + get_image_extension(results[x].url)
                with open(path, 'wb') as handler:
                    handler.write(results[x].content)
                results[x].close()
            else:
                print('Request at index {} failed'.format(x))


def get_images(filepath='../HuJuData/data/processed/image_urls.csv', incomplete_urls=None,
               incomplete_ids=None, batch_size=50, _max=None, start_index=0):
    def batch_instance(retry=False):
        if filepath is not None and retry is False:
            with open(filepath, 'r', encoding='utf-8') as file_handler:
                df = pd.read_csv(file_handler)
                print('Fetching images from index {} to {} of {}'.format(start_index, start_index + batch_size, _max - start_index))
                image_fetch = ImageFetcher(df['id'][start_index:start_index + batch_size],
                                           df['url'][start_index:start_index + batch_size])
                return image_fetch
        if filepath is not None and retry is True:
            image_fetch = ImageFetcher(incomplete_ids, incomplete_urls)
            return image_fetch

    if incomplete_urls is None:
        fetcher = batch_instance()
    else:
        fetcher = batch_instance(retry=True)

    fetcher.get(limit=50)

    if fetcher.incompleteID is not None:
        num_successful = batch_size - len(fetcher.incompleteID)
        print("Fetched {} images, but failed {}".format(num_successful, len(fetcher.incompleteID)))
        print('Retrying failed requests ...')
        time.sleep(5)
        get_images(batch_size=batch_size, start_index=start_index, _max=_max,
                   incomplete_urls=fetcher.incompleteURL, incomplete_ids=fetcher.incompleteID)

    try:
        fetcher.ids = set(fetcher.ids) - set(fetcher.incompleteID)
    except TypeError:
        print('No failed requests')

    resize_images(list(fetcher.ids))


def image_fetcher(start_index=0, batch_size=50, _max=None):
    const_batch_size = batch_size
    const_start = start_index
    _max = const_start + _max
    while True:
        if start_index is _max:
            return False
        elif _max is None:
            get_images(batch_size=batch_size, start_index=start_index)
            start_index += const_batch_size
        else:
            get_images(batch_size=batch_size, start_index=start_index, _max=_max)
            start_index += const_batch_size


if __name__ == '__main__':
    start = time.time()

    # main(batch_size=100000)
    # extract_only_image_urls(batch_size=200000)
    image_fetcher(batch_size=100, start_index=303000, _max=5000)

    end = time.time()
    time = end - start
    print("Process took ~{:.3g} minutes".format(int(time) / 60))
