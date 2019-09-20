#!/usr/bin/env python

import json_lines as jl
import json
import requests
import time


def main(num_of_articles):
    articles = []
    with open('../HuJuData/data/data/TREC_Washington_Post_collection.v2.jl', 'rb') as f:
        num = 1
        for item in jl.reader(f):
            if item['type'] == "article":
                if image_exists(item):
                    get_images(item)
                    articles.append(item)
                    print(num, 'of', num_of_articles)
                    num += 1
            if len(articles) == num_of_articles:
                print('Limit reached')
                break
        f.close()
    return articles


# Writes the data to a json file
def write_to_file(articles):
    with open('../HuJuData/data/data/snippet.json', 'w', encoding='utf-8') as file_handler:
        for data in articles:
            file_handler.write(json.dumps(data, indent=4, ensure_ascii=False))

        print('Wrote to file')
        file_handler.close()


# Fetches images by URL on the current article.
def get_images(current_article):
    for content in current_article['contents']:
        if 'fullcaption' in content:
            img_data = requests.get(content['imageURL']).content
            with open('../HuJuData/data/data/images/' + current_article['id'] + '.jpg', 'wb') as handler:
                handler.write(img_data)
                print('Successfully downloaded image', current_article['id'])
                return True


# Checks if content-object is of type image, and if it's the main image of the article (by presence of fullcaption)
def image_exists(current_article):
    for content in current_article['contents']:
        if content['type'] == 'image':
            if 'fullcaption' in content:
                if len(content['fullcaption']) > 0:
                    return True


if __name__ == '__main__':
    start = time.time()

    data = main(1000)
    write_to_file(data)

    end = time.time()

    time = end - start

    print('Process took ~%.3g minutes' % int(time/60))
