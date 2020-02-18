#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A script to clean and improve the TREC Washington Post Corpus for use in research. Creates a CSV file.
import os
import re
from datetime import datetime as dt
from warnings import filterwarnings

import pandas as pd
import pytz
from bs4 import BeautifulSoup
from json_lines import reader as jl_reader

import categories
from utils import options, file_len, rindex


def main():
    if os.path.exists(twpc_options.save_path):
        twpc_options.save_path = options(twpc_options.save_path)
        print('New path: {}'.format(twpc_options.save_path))
    articles, num = [], 0
    _max = file_len(twpc_options.source_path) - 1
    with open(twpc_options.source_path, 'rb') as f:
        for article in jl_reader(f):
            if article is None:
                continue
            article['date'], article['time'] = unix_to_dt(article)
            article['image_url'] = get_image_url(article)
            article['author_bio'] = get_author_bio(article)
            article['category'], article['subcategory'] = get_categories(article)
            if article['title'] is None or article['title'] == '':
                article['title'] = 'NaN'
            if article['author'] is None or article['author'] == '':
                article['author'] = get_author(article)
            if is_compilation(article):
                article['subtype'] = 'compilation'
            else:
                article['subtype'] = 'standalone'
            remove_unwanted_properties(article)
            articles.append(article)
            num += 1
            if num % twpc_options.batch_size == 0 or num == _max:
                save_as_csv(articles, path=twpc_options.save_path)
                articles = []
                print('Processed {} of {} articles'.format(num, _max))
                if num == _max:
                    print('Process completed')
                    return


def remove_unwanted_properties(article):
    for prop in twpc_options.unwanted_properties:
        del article[prop]


# Finds the appropriate main category group and returns this
def get_categories(article):
    for prop in article['contents']:
        if prop is not None and 'type' in prop and prop['type'] == 'kicker' \
                and 'content' in prop and prop['content'] is not None:
            return categories.get_group(prop['content']), html_to_text(prop['content'])
    return 'NaN', 'NaN'


# Gets author bio from content array
def get_author_bio(article):
    for prop in article['contents']:
        if prop is not None and 'bio' in prop and prop['bio'] != '':
            return html_to_text(prop['bio'])
    return 'NaN'


def is_compilation(article):
    for prop in article['contents']:
        if prop is not None and 'content' in prop and str(prop['content']).__contains__('Compiled by'):
            return prop
    return False


# Gets author if not present in article (typically if it's a compilation-type blog post)
def get_author(article):
    proceed = is_compilation(article)
    if proceed is not False:
        clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        clean_text = str(re.sub(clean, '', proceed['content'])).split()
        i = rindex(clean_text, 'by')
        return ' '.join(clean_text[i + 1:])
    return 'NaN'


# Fetches image URL on the current article.
def get_image_url(article):
    for prop in article['contents']:
        if prop is not None and prop['type'] == 'image':
            return str(prop['imageURL']) if prop['imageURL'] != '' else 'NaN'
    return 'NaN'


# Convert unix dates to datetime string
def unix_to_dt(item):
    try:
        item['date'] = dt.utcfromtimestamp(item['published_date'] / 1000.0) \
            .astimezone(pytz.timezone("America/New_York"))
        item['time'] = item['date'].strftime('%H-%M-%S')
        item['date'] = item['date'].strftime('%Y-%m-%d')
        return item['date'], item['time']
    except TypeError:
        print('Unable to convert {}, id: {} '.format(item['published_date'], item['id']))
        return 'NaN', 'NaN'
    except OSError:
        print('Invalid argument {}, id: {}'.format(item['published_date'], item['id']))
        return 'NaN', 'NaN'


# Finds "content" strings within objects in an array and concatenates to a single string
def stringify(articles):
    html_breaklines = '<br><br>' if twpc_options.breaklines is True else ''
    for article in articles:
        content_array = []
        for content in article['contents']:
            if content is not None:
                if 'subtype' in content and content['subtype'] == 'paragraph':
                    content_array.append(html_to_text(content['content']) + html_breaklines)
        del article['contents']
        content_string = ' '.join(content_array).replace('\n', '')
        article['text'] = content_string
    return articles


def html_to_text(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.text


# Saves data as csv
def save_as_csv(data, path):
    processed_data = stringify(data)
    df = pd.DataFrame(processed_data)
    if twpc_options.drop_na is True:
        df = df.dropna()
    if os.path.exists(path):
        df.to_csv(path, sep=',', index=False, header=False, mode='a')
    else:
        df.to_csv(path, sep=',', index=False, header=True, mode='w')


# Class to set options used in the program
class TWPCOptions:
    def __init__(self, source_path, save_path, breaklines=None, drop_na=None, batch_size=None, unwanted_properties=None):
        self.breaklines = False if breaklines is None else True
        self.drop_na = False if drop_na is None else True
        self.batch_size = 10000 if batch_size is None else batch_size
        self.unwanted_properties = ('source', 'published_date') if unwanted_properties is None else unwanted_properties
        self.source_path = source_path
        self.save_path = save_path


if __name__ == '__main__':
    filterwarnings("ignore", category=UserWarning, module='bs4')  # Suppress userwarnings
    twpc_options = TWPCOptions(
        source_path='E:\\data\\TWPC.jl',
        save_path='E:\\data\\twp_corpus.csv',
        batch_size=50000
    )
    main()
