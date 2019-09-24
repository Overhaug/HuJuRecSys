#!/usr/bin/env python
# A script to extract data from the Washington Post corpus, as well as images attached to the articles

import json_lines as jl
import json
import time
import grequests


def main(num_of_articles, batch):
    articles = []
    with open('../HuJuData/data/TREC_Washington_Post_collection.v2.jl', 'rb') as f:
        article_sublist = []
        num = 0
        for item in jl.reader(f):
            if item['type'] == "article":
                img_url = get_image_url(item)
                if img_url is not None:
                    article_sublist.append(
                        {'id': item['id'], 'url': get_image_url(item)})  # temp list to make requests easier
                    articles.append(item)

                    if len(article_sublist) == batch:
                        fetcher = ImageFetcher((x['url'] for x in article_sublist),
                                               (y['id'] for y in article_sublist))

                        print('Fetching images ...')
                        started = time.time()
                        fetcher.get()

                        num_of_images = batch
                        if len(fetcher.incomplete) > 0:
                            articles = remove_failed_requests(fetcher.incomplete, articles)
                            num_of_images -= len(fetcher.incomplete)
                        print("Fetched {} images in {} seconds".format(num_of_images, time.time() - started))

                        article_sublist = []

                        num += batch
                        print(num, 'of', num_of_articles)
                        if len(articles) == num_of_articles:
                            print('Limit reached')
                            break
        f.close()
    return articles


def remove_failed_requests(failed, article_data):
    for item in article_data:
        url = get_image_url(item)
        if url in failed:
            article_data.remove(item)
            print("Removed object corresponding to failed request")
    return article_data


# Writes the data to a json file
def write_to_file(articles):
    with open('../HuJuData/data/snippetTest.json', 'w', encoding='utf-8') as file_handler:
        for item in articles:
            file_handler.write(json.dumps(item, indent=2, ensure_ascii=False))

        print('Wrote to file')
        file_handler.close()


# Fetches images by URL on the current article.
def get_image_url(current_article):
    for content in current_article['contents']:
        if content['type'] == 'image':
            if 'fullcaption' in content:
                if len(content['fullcaption']) > 0:
                    return str(content['imageURL'])


class ImageFetcher:
    def __init__(self, url, ids):
        self.ids = [x for x in ids]
        self.urls = [x for x in url]
        self.incomplete = []

    def exception(self, request, exception):
        print("Problem: {}: {}".format(request.url, exception))
        self.incomplete.append(request.url)
        index = self.urls.index(request.url)
        print(index)
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
                    #print('Successfully downloaded image', self.ids[x])
                else:
                    print('Object at index {} failed'.format(x))


if __name__ == '__main__':
    start = time.time()

    data = main(num_of_articles=3000, batch=500)
    write_to_file(data)

    end = time.time()

    time = end - start

    print("Process took ~{:.3g} minutes {}".format(int(time) / 60, time))
