#!/usr/bin/env python
# A script to extract data from the Washington Post corpus, as well as images attached to the articles

import json
import time
from datetime import datetime as dt

import grequests
import json_lines as jl
import pandas as pd
import pytz
import re
import os
from zipfile import ZipFile
from PIL import Image


def main(_max=0, batch_size=5000, images=False, path='../HuJuData/data/corpus/TREC_Washington_Post_collection.v2.jl'):
    articles = []
    num = 0
    with open(path, 'rb') as f:
        article_sublist = []
        for article in jl.reader(f):
            article = convert_unix_to_datetime(article)
            article = add_image_url(article)
            article = remove_type_from_object(article)

            if article is not None:
                articles.append(article)  # There are a handful of empty objects in the dataset
            else:
                continue
            if len(articles) == batch_size:
                num_of_items = batch_size
                if images:
                    get_images(article_sublist, articles, num_of_items)
                article_sublist = []

                num += num_of_items
                if _max is not 0:
                    print(num, 'of', _max)
                else:
                    print('Processed {} articles'.format(num))
                get_as_csv(get_image_url(articles), path='../HuJuData/data/processed/image_urls.csv', convert=False)
                get_as_csv(articles, path='../HuJuData/data/processed/corpus_csv.csv')
                articles = []
                if _max - num in range(-25, 25):
                    break
    f.close()
    return articles


def get_images(filepath='../HuJuData/data/processed/image_urls.csv', incompleteURL=None,
               incompleteID=None, batch_size=50, _max=None):
    print('Fetching images ...')
    global _start

    def batch_instance(retry=False, incompleteURL=incompleteURL, incompleteID=incompleteID):
        if filepath is not None and retry is False:
            with open(filepath, 'r', encoding='utf-8') as file_handler:
                df = pd.read_csv(file_handler)
                print(_start, _max, batch_size)
                image_fetch = ImageFetcher(df['id'][_start:_start+batch_size], df['url'][_start:_start+batch_size])
                return image_fetch
        if filepath is not None and retry is True:
            image_fetch = ImageFetcher(incompleteID, incompleteURL)
            return image_fetch

    if incompleteURL is None:
        fetcher = batch_instance()
    else:
        fetcher = batch_instance(retry=True)

    started = time.time()
    fetcher.get()

    num = 0
    if fetcher.incompleteID is not None:
        num -= len(fetcher.incompleteID)
        print("Fetched {} images in {} seconds".format(num, time.time() - started))

        print('{}'.format(len(fetcher.incompleteID)))
        print('Trying again')
        get_images(incompleteURL=fetcher.incompleteURL, incompleteID=fetcher.incompleteID)

    resize_images(fetcher.ids)


CONST_BATCH_SIZE = 0
_start = 0
def image_fetcher(batch_size=50, _max=None):
    global CONST_BATCH_SIZE
    CONST_BATCH_SIZE = batch_size
    global _start
    while True:
        if _max is None:
            get_images(batch_size=batch_size)
        elif _max is _start:
            break
        else:
            get_images(batch_size=batch_size, _max=_max)
        _start += CONST_BATCH_SIZE


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
    urls = []
    for content in current_article['contents']:
        if content is not None and content['type'] == 'image':
            if content['imageURL'] not in urls:
                urls.append(str(content['imageURL']))
                return str(content['imageURL'])


# Convert unix dates to datetime string
def convert_unix_to_datetime(item):
    try:
        item['published_date'] = dt.utcfromtimestamp(item['published_date'] / 1000.0) \
            .astimezone(pytz.timezone("America/New_York")) \
            .strftime('%Y-%m-%d')
    except TypeError:
        print('Unable to convert {} '.format(item['published_date']))
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
    simple_urls = []
    for index in range(len(article)):
        urls = {}
        num = 0
        for content in article[index]['contents']:
            if content is not None and content['type'] == 'image':
                if content['imageURL'] not in simple_urls:
                    urls['id'] = article[index]['id'] + '-' + str(num)
                    urls['url'] = content['imageURL']
                    urls_list.append(urls)
                    num += 1
                    urls = {}
    return urls_list


# Writes data as csv
def get_as_csv(data, path, convert=True):
    if convert:
        processed_data = from_array_to_string(data)
        df = pd.DataFrame(processed_data)
    else:
        df = pd.DataFrame(data)

    if os.path.exists(path):
        with open(path, 'a', encoding='utf-8') as existing_file:
            df.to_csv(existing_file, sep=',', index=False, header=False)
    else:
        with open(path, 'w', encoding='utf-8') as new_file:
            df.to_csv(new_file, sep=',', index=False, header=True)


# Extract all content objects (in a json array) of type paragraph to a single string
# passed list looks like this:
# [
#    {
#        'id': '19239-123-fw-efwf-1231',
#        .....
#        'contents':
#            {
#                'type': 'santized_html',
#                'subtype': 'paragraph',
#            }
#    }
# ]
def from_array_to_string(articles):
    content_string = ''

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
                content_string = ''
    return articles


def remove_urls_from_text(article):
    article = article.split()
    new_string = ' '
    for word in range(len(article)):
        if article[word].startswith('http') \
                or article[word].endswith('>') \
                or article[word].startswith('<'):
            if article[word].__contains__('>'):
                word_list = article[word].split('>')
                word_list.remove(word_list[0])
                index = article.index(article[word])
                s = ''
                s.join(word_list)
                article.insert(index, s)
            else:
                article.insert(word, '')
    return new_string.join(article)


def html_to_text(text):
    clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    return str(re.sub(clean, ' ', text))


def resize_images(ids):
    files = []
    filenames = []

    d = '../HuJuData/data/processed/images/'
    for path in os.listdir(d):
        full_path = os.path.join(d, path)
        if os.path.isfile(full_path) and path in ids and str(full_path).endswith('jpeg'):
            files.append(full_path)
            filenames.append(path)

    size = 400, 400
    for img in files:
        try:
            im = Image.open(img)
            im.thumbnail(size, Image.ANTIALIAS)
            index = files.index(img)
            im.save(d+filenames[index], "JPEG")
        except IOError:
            print('Could not resize {}'.format(img))


# Downloads images from a given list of urls
# Filenames equate to article ID
class ImageFetcher:
    def __init__(self, ids, url, incompleteURL=None, incompleteID=None):
        self.incompleteURL = incompleteURL
        self.incompleteID = incompleteID
        if incompleteID is not None:
            self.ids = [x for x in incompleteID]
            self.urls = [x for x in incompleteURL]
        else:
            self.ids = [x for x in ids]
            self.urls = [x for x in url]

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))
        self.urls.append(request.url)
        self.ids.append(self.urls.index(request.url))

    def get(self, limit=50):
        results = grequests.map((grequests.get(u) for u in self.urls),
                                exception_handler=self.exception,
                                size=limit,
                                stream=False)
        for x in range(len(self.urls)):
            path = '../HuJuData/data/processed/images/' + self.ids[x] + '.jpeg'
            with open(path, 'wb') as handler:
                if results[x] is not None:
                    handler.write(results[x].content)
                    results[x].close()
                else:
                    print('Request at index {} failed'.format(x))


def extract_only_image_urls(path='../HuJuData/data/corpus/TREC_Washington_Post_collection.v2.jl', batch_size=20000):
    articles = []
    num = 0
    with open(path, 'rb') as file_reader:
        for article in jl.reader(file_reader):
            articles.append(article)
            if len(articles) == batch_size:
                get_as_csv(get_image_url(articles), path='../HuJuData/data/processed/image_urls.csv', convert=False)
                num += len(articles)
                articles = []
                print(num)


if __name__ == '__main__':
    start = time.time()

    #main(batch_size=50000, _max=0)
    # extract_only_image_urls(batch_size=50000)
    # get_images(batch_size=10, _max=1000)
    image_fetcher(batch_size=100, _max=1000)

    end = time.time()

    time = end - start

    print("Process took ~{:.3g} minutes".format(int(time) / 60))
