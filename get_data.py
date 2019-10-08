#!/usr/bin/env python
# A script to extract data from the Washington Post corpus, as well as images attached to the articles

import json
import time
from datetime import datetime as dt
import pytz

import grequests
import json_lines as jl


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


# Convert unix dates to datetime string
def convert_unix_to_datetime(item):
    item['published_date'] = dt.utcfromtimestamp(item['published_date'] / 1000.0)\
        .astimezone(pytz.timezone("America/New_York"))\
        .strftime('%Y-%m-%d')
    return item


def remove_failed_objects(failed, article_data):
    for item in article_data:
        url = get_image_url(item)
        if url in failed:
            article_data.remove(item)
            print("Removed object corresponding to failed request")
    return article_data


# Writes the data to a json file
# Modifies the file to be json serializable
def write_to_file(articles):
    with open('../HuJuData/data/snippetTest.json', 'w', encoding='utf-8') as file_handler:
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
                                size=500,
                                stream=False)
        for x in range(len(self.urls)):
            with open('../HuJuData/data/images/' + self.ids[x] + '.jpg', 'wb') as handler:
                if results[x] is not None:
                    handler.write(results[x].content)
                    results[x].close()
                else:
                    print('Request at index {} failed'.format(x))


if __name__ == '__main__':
    start = time.time()

    data = main(_max=1000, batch_size=500)
    write_to_file(data)

    end = time.time()

    time = end - start

    print("Process took ~{:.3g} minutes".format(int(time) / 60))
