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
from . import categories
from datautils import utils
from json_lines import reader as jlreader


def main(path, batch_size=5000, save_loc='TWPC_cleaned.csv'):
    if os.path.exists(save_loc):
        save_loc = utils.options(save_loc)
        print('New path: {}'.format(save_loc))
    articles, num = [], 0
    _max = utils.file_len(path) - 1
    with open(path, 'rb') as f:
        for article in jlreader(f):
            if article is None:
                continue
            article['date'], article['time'] = convert_unix_to_date_time(article)
            article['image_url'] = get_image_url(article)
            article['author_bio'] = get_author_bio(article)
            article['category'], article['subcategory'] = get_categories(article)
            if article['title'] is None or article['title'] == '':
                article['title'] = 'nan'
            if article['author'] is None or article['author'] == '':
                article['author'] = get_author(article)
            if is_compilation(article):
                article['subtype'] = 'compilation'
            else:
                article['subtype'] = 'standalone'

            articles.append(article)
            num += 1
            if num % batch_size == 0 or num == _max:
                save_as_csv(articles, path=save_loc)
                articles = []
                print('Processed {} of {} articles'.format(num, _max))
                if num == _max:
                    print('Process completed')
                    return


# Finds the appropriate main category group and returns this
def get_categories(article):
    for prop in article['contents']:
        if prop is not None and 'type' in prop and prop['type'] == 'kicker' \
                and 'content' in prop and prop['content'] is not None:
            return categories.get_group(prop['content']), html_to_text(prop['content'])
    return 'nan', 'nan'


# Gets author bio from content array
def get_author_bio(article):
    for prop in article['contents']:
        if prop is not None and 'bio' in prop and prop['bio'] != '':
            return html_to_text(prop['bio'])
    return 'nan'


def is_compilation(article):
    for prop in article['contents']:
        if prop is not None and 'content' in prop and str(prop['content']).__contains__('Compiled by'):
            return prop
    return False


# Gets author if not present in article (typically if it's a compilation-type blog post)
def get_author(article):
    proceed = is_compilation(article)
    if proceed:
        clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        clean_text = str(re.sub(clean, '', proceed['content'])).split()
        i = utils.rindex(clean_text, 'by')
        return ' '.join(clean_text[i + 1:])
    return 'nan'


# Fetches image URL on the current article.
def get_image_url(article):
    for prop in article['contents']:
        if prop is not None and prop['type'] == 'image':
            return str(prop['imageURL']) if prop['imageURL'] != '' else 'nan'
    return 'nan'


# Convert unix dates to datetime string
def convert_unix_to_date_time(item):
    try:
        item['date'] = dt.utcfromtimestamp(item['published_date'] / 1000.0) \
            .astimezone(pytz.timezone("America/New_York")) \
            .strftime('%Y-%m-%d')
        item['time'] = dt.utcfromtimestamp(item['published_date'] / 1000.0) \
            .astimezone(pytz.timezone("America/New_York")) \
            .strftime('%H-%M-%S')
        del item['published_date']
        return item['date'], item['time']
    except TypeError:
        print('Unable to convert {}, id: {} '.format(item['published_date'], item['id']))
        return 'nan', 'nan'
    except OSError:
        print('Invalid argument {}, id: {}'.format(item['published_date'], item['id']))
        return 'nan', 'nan'


# Finds "content" strings within objects in an array and concatenates to a single string
def stringify(articles, breaklines=True):
    content_array = []
    html_breaklines = '<br><br>' if breaklines is True else ''
    for article in articles:
        for content in article['contents']:
            if content is not None and 'content' in content:
                if 'subtype' in content and content['subtype'] == 'paragraph':
                    content_array.append(html_to_text(content['content']) + html_breaklines)
        del article['contents']
        content_string = ' '.join(content_array).replace('\n', '')
        article['text'] = content_string
        content_array = []
    return articles


def html_to_text(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.text


# Saves data as csv
def save_as_csv(data, path):
    processed_data = stringify(data, breaklines=False)
    df = pd.DataFrame(processed_data).dropna()
    if os.path.exists(path):
        df.to_csv(path, sep=',', index=False, header=False, mode='a')
    else:
        df.to_csv(path, sep=',', index=False, header=True, mode='w')


if __name__ == '__main__':
    filterwarnings("ignore", category=UserWarning, module='bs4')  # Suppress userwarnings
    main(batch_size=300000,
         path='E:\\data\\TWPC.jl',
         save_loc='E:\\data\\corpus_wo_breaklines.csv')
