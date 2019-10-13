#!/usr/bin/env python
# A script to extract data from the Washington Post corpus, as well as images attached to the articles

import json
import time
from datetime import datetime as dt

import grequests
import json_lines as jl
import pandas as pd
import pytz


def main(_max, batch_size):
    articles = []
    num = 0
    with open('../HuJuData/data/TREC_Washington_Post_collection.v2.jl', 'rb') as f:
        article_sublist = []
        for article in jl.reader(f):
            if article['type'] == "article":
                img_url = get_image_url(article)
                if img_url is not None:
                    article_sublist.append(
                        {'id': article['id'], 'url': get_image_url(article)})  # temp list to make requests easier

                    article = convert_unix_to_datetime(article)
                    article = add_image_url(article)
                    article = remove_type_from_object(article)

                    articles.append(article)

                    if len(article_sublist) == batch_size:
                        fetcher = ImageFetcher((x['url'] for x in article_sublist),
                                               (y['id'] for y in article_sublist))

                        print('Fetching images ...')
                        started = time.time()
                        fetcher.get()

                        num_of_items = batch_size
                        if len(fetcher.incomplete) > 0:
                            articles = remove_failed_objects(fetcher.incomplete, articles)
                            num_of_items -= len(fetcher.incomplete)
                        print("Fetched {} images in {} seconds".format(num_of_items, time.time() - started))

                        article_sublist = []

                        num += num_of_items
                        print(num, 'of', _max)
                        if _max - len(articles) in range(0, 25):
                            print('Finished fetching data ...')
                            break
        f.close()
    return articles


# Removes "type" property from object
def remove_type_from_object(item):
    del item['type']
    return item


# Adds image url from content array to root level
def add_image_url(item):
    url = get_image_url(item)
    item['image_url'] = url
    return item


# Convert unix dates to datetime string
def convert_unix_to_datetime(item):
    item['published_date'] = dt.utcfromtimestamp(item['published_date'] / 1000.0)\
        .astimezone(pytz.timezone("America/New_York"))\
        .strftime('%Y-%m-%d')
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
    with open('../HuJuData/data/snippetTest2.json', 'w', encoding='utf-8') as file_handler:
        file_handler.write('[')
        for item in articles:
            file_handler.write(json.dumps(item, indent=2, ensure_ascii=False))
            if item != articles[-1]:
                file_handler.write(',')
        file_handler.write(']')

        print('Wrote to file {}'.format(file_handler.name))
        file_handler.close()


# Fetches image URL on the current article.
def get_image_url(current_article):
    for content in current_article['contents']:
        if content['type'] == 'image':
            if 'fullcaption' in content:
                if len(content['fullcaption']) > 0:
                    return str(content['imageURL'])


# Writes data as csv
def get_as_csv(d):
    f = from_array_to_string(d)

    df = pd.DataFrame(f)
    df.to_csv('../HuJuData/data/snippetCSV2.csv', sep=',', index=False)


# Extract all content objects (in a json array) of type paragraph to a single string
def from_array_to_string(d):
    content_string = ''

    for x in d:
        for k, v in x.items():
            if k == 'contents':
                for i in v:
                    for e, h in i.items():
                        if e == 'subtype' and h == 'paragraph':
                            content_string += i['content']
                x.pop(k)
                x['text'] = content_string
                content_string = ''
    return d


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
            with open('../HuJuData/data/images/' + self.ids[x] + '.jpg', 'wb') as handler:
                if results[x] is not None:
                    handler.write(results[x].content)
                    results[x].close()
                else:
                    print('Request at index {} failed'.format(x))


if __name__ == '__main__':
    start = time.time()

    get_as_csv(main(_max=250, batch_size=50))

    end = time.time()

    time = end - start

    print("Process took ~{:.3g} minutes".format(int(time) / 60))
