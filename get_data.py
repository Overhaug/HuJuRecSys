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


def main(_max=0, batch_size=5000, images=False):
    articles = []
    num = 0
    with open('../HuJuData/data/corpus/TREC_Washington_Post_collection.v2.jl', 'rb') as f:
        article_sublist = []
        for article in jl.reader(f):
            article = convert_unix_to_datetime(article)
            article = add_image_url(article)
            article = remove_type_from_object(article)
            
            if article is not None:
                articles.append(article)
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
                #get_as_csv(articles, path='../HuJuData/data/processed/corpus_csv.csv')
                articles = []
                if _max - num in range(-25, 25):
                    break
    f.close()
    return articles


def get_images(article_sublist, articles, num):
    fetcher = ImageFetcher((x['url'] for x in article_sublist),
                           (y['id'] for y in article_sublist))

    print('Fetching images ...')
    started = time.time()
    fetcher.get()

    if len(fetcher.incomplete) > 0:
        articles = remove_failed_objects(fetcher.incomplete, articles)
        num -= len(fetcher.incomplete)
    print("Fetched {} images in {} seconds".format(num, time.time() - started))
    return len(articles)


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
        num = 0
    return urls_list


# Writes data as csv
def get_as_csv(d, path, convert=True):
    if convert:
        f = from_array_to_string(d)
        df = pd.DataFrame(f)
    else:
        df = pd.DataFrame(d)

    if os.path.exists(path):
        with open(path, 'a', encoding='utf-8') as x:
            df.to_csv(x, sep=',', index=False, header=False)
    else:
        with open(path, 'w', encoding='utf-8') as f:
            df.to_csv(f, sep=',', index=False, header=True)


# Extract all content objects (in a json array) of type paragraph to a single string
def from_array_to_string(d):
    content_string = ''

    for x in d:
        for k, v in x.items():
            if k == 'contents':
                for i in v:
                    if i is not None:
                        for e, h in i.items():
                            if e == 'subtype' and h == 'paragraph':
                                plain_text = html_to_text(i['content'])
                                content_string += plain_text
                x.pop(k)
                x['text'] = content_string
                content_string = ''
    return d


def html_to_text(text):
    clean = re.compile('<.*?>')
    return str(re.sub(clean, '', text))


# Downloads images from a given list of urls
# Filenames equate to article ID
class ImageFetcher:
    def __init__(self, url, ids):
        self.ids = [x for x in ids]
        self.urls = [x for x in url]
        self.incomplete = []

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))
        self.incomplete.append(request.url)
        index = self.urls.index(request.url)
        del self.ids[index]
        del self.urls[index]

    def get(self):
        results = grequests.map((grequests.get(u) for u in self.urls),
                                exception_handler=self.exception,
                                size=50,
                                stream=True)
        for x in range(len(self.urls)):
            with open('../HuJuData/data/processed/images/' + self.ids[x] + '.jpg', 'wb') as handler:
                if results[x] is not None:
                    handler.write(results[x].content)
                    results[x].close()
                else:
                    print('Request at index {} failed'.format(x))


if __name__ == '__main__':
    start = time.time()

    main(batch_size=30000, _max=0)

    end = time.time()

    time = end - start

    print("Process took ~{:.3g} minutes".format(int(time) / 60))
