#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A script to clean and improve the TREC Washington Post Corpus for use in research. Creates a CSV file.

import re
from datetime import datetime as dt
from os.path import exists
from warnings import filterwarnings

import pandas as pd
import pytz
from bs4 import BeautifulSoup
from json_lines import reader as jlreader

import utils


def main(path, _max=None, batch_size=5000, save_loc='TWPC_cleaned.csv'):
    if exists(save_loc):
        save_loc = utils.options(save_loc)
        print('New path: {}'.format(save_loc))
    articles = []
    num = 0
    _max = utils.file_len(path) - 1 if _max is None else _max
    with open(path, 'rb') as f:
        for article in jlreader(f):
            if article is None:
                continue
            article = convert_unix_to_datetime(article)
            article = get_image_url(article)
            article = get_author_bio(article)
            article = get_topic(article)
            if article['title'] is None or article['title'] == '':
                # Some way to infer a title?
                article['title'] = 'nan'
            if article['author'] is None or article['author'] == '':
                article = get_author(article)
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


# Extracts topic from article kickers. They are usually in either of these formats: "Business", "Redskins/NFL"
def get_topic(article):
    for prop in article['contents']:
        if prop is not None and 'type' in prop and prop['type'] == 'kicker' \
                and 'content' in prop and prop['content'] is not None:
            article['topic'] = html_to_text(prop['content'])
            return article
    article['topic'] = 'nan'
    return article


# Gets author bio from content array
def get_author_bio(article):
    for prop in article['contents']:
        if prop is not None and 'bio' in prop and prop['bio'] != '':
            article['author_bio'] = html_to_text(prop['bio'])
            return article
    article['author_bio'] = 'nan'
    return article


# Gets author if not present in article (typically if it's a compilation-type blog post)
def get_author(article):
    for prop in article['contents']:
        if prop is not None and 'content' in prop and str(prop['content']).__contains__('Compiled by'):
            clean = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
            clean_text = str(re.sub(clean, '', prop['content'])).split()
            i = utils.rindex(clean_text, 'by')
            article['author'] = ' '.join(clean_text[i + 1:])
            return article
    article['author'] = 'nan'
    return article


# Fetches image URL on the current article.
def get_image_url(article):
    for prop in article['contents']:
        if prop is not None and prop['type'] == 'image':
            article['image_url'] = str(prop['imageURL']) if prop['imageURL'] != '' else 'nan'
            return article
    article['image_url'] = 'nan'
    return article


# Convert unix dates to datetime string
def convert_unix_to_datetime(item):
    try:
        item['published_date'] = dt.utcfromtimestamp(item['published_date'] / 1000.0) \
            .astimezone(pytz.timezone("America/New_York")) \
            .strftime('%Y-%m-%d')
    except TypeError:
        print('Unable to convert {}, id: {} '.format(item['published_date'], item['id']))
        item['published_date'] = 'nan'
    except OSError:
        print('Invalid argument {}, id: {}'.format(item['published_date'], item['id']))
    return item


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
    processed_data = stringify(data)
    df = pd.DataFrame(processed_data)
    df.to_csv(path, sep=',', index=False, header=True, mode='w')


if __name__ == '__main__':
    filterwarnings("ignore", category=UserWarning, module='bs4')  # Suppress userwarnings
    main(batch_size=50000,
         path='../HuJuData/data/corpus/TWPC.jl',
         save_loc='../HuJuData/data/processed/corpus_csv.csv')
