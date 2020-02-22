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
        print("New path: {}".format(twpc_options.save_path))
    articles = []
    _max = file_len(twpc_options.source_path) - 1
    with open(twpc_options.source_path, "rb") as f:
        for n, article in enumerate(jl_reader(f), start=1):
            if article is None:
                continue
            article["date"], article["time"] = unix_to_dt(article)
            article["image_url"], article["image_caption"] = get_image_url_and_caption(article)
            article["author_bio"] = get_author_bio(article)
            article["category"], article["subcategory"] = get_categories(article)
            if article["title"] is None or article["title"] == "":
                article["title"] = "NaN"
            if article["author"] is None or article["author"] == "":
                article["author"] = get_author(article)
            if is_compilation(article):
                article["subtype"] = "compilation"
            else:
                article["subtype"] = "standalone"
            article["text"] = stringify(article)
            remove_unwanted_properties(article)
            articles.append(article)
            if n % twpc_options.batch_size == 0 or n == _max:
                save_as_csv(articles)
                articles = []
                print("Processed {} of {} articles".format(n, _max))
                if n == _max:
                    print("Process completed")
                    return


def remove_unwanted_properties(article):
    for prop in twpc_options.unwanted_properties:
        del article[prop]
    del article["contents"]


# Finds the appropriate main category group and returns this
def get_categories(article):
    for prop in article["contents"]:
        if prop is not None and "type" in prop and prop["type"] == "kicker" \
                and "content" in prop and prop["content"] is not None:
            return categories.get_group(prop["content"]), parse_text(prop["content"])
    return "NaN", "NaN"


# Gets author bio from content array
def get_author_bio(article):
    for prop in article["contents"]:
        if prop is not None and "bio" in prop and prop["bio"] != "":
            return parse_text(prop["bio"])
    return "NaN"


def is_compilation(article):
    for prop in article["contents"]:
        if prop is not None and "content" in prop and str(prop["content"]).__contains__("Compiled by"):
            return prop
    return False


# Gets author if not present in article (typically if it"s a compilation-type blog post)
def get_author(article):
    proceed = is_compilation(article)
    if proceed is not False:
        clean = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
        clean_text = str(re.sub(clean, "", proceed["content"])).split()
        i = rindex(clean_text, "by")
        return " ".join(clean_text[i + 1:])
    return "NaN"


# Assumes that the first content-blob found with a fullcaption and image URL is the "main" image of the article/blog
def get_image_url_and_caption(article):
    for prop in article["contents"]:
        if prop is not None and prop["type"] == "image":
            if "fullcaption" in prop and prop["fullcaption"] != "" and prop["imageURL"] != "":
                return prop["imageURL"], parse_text(prop["fullcaption"])
    return "NaN", "NaN"


# Convert unix dates to datetime string
def unix_to_dt(item):
    try:
        item["date"] = dt.utcfromtimestamp(item["published_date"] / 1000.0) \
            .astimezone(pytz.timezone("America/New_York"))
        item["time"] = item["date"].strftime("%H:%M:%S")
        item["date"] = item["date"].strftime("%Y-%m-%d")
        return item["date"], item["time"]
    except TypeError:
        print("Unable to convert {}, id: {} ".format(item["published_date"], item["id"]))
        return "NaN", "NaN"
    except OSError:
        print("Invalid argument {}, id: {}".format(item["published_date"], item["id"]))
        return "NaN", "NaN"


# Finds relevant content in the contents-array found in articles
# It is difficult to know exactly what can be found in the WP dataset, so we are definitely not capturing everything.
def stringify(article):
    content_array = []
    for content in filter(None, article["contents"]):
        if content["type"] == "sanitized_html":
            # Some articles have manually inserted "Read more" sections, which we do not want
            if str(content['content']).lower().__contains__("read more"):
                break  # We assume that if the object matches the condition, we are at the end of the article
            content_array.append(parse_text(content["content"]))
        elif content["type"] == "list":
            for item in content["content"]:
                content_array.append(parse_text(item))
        elif twpc_options.mode == "html":
            if content["type"] == "video" and "content" in content:
                content_array.append(create_video_block(content))
            elif content["type"] == "tweet":
                content_array.append(create_tweet_block(content))
        elif content["type"] == "tweet":
            content_array.append(parse_text(content["content"]["text"]))
            content_array.append(parse_text(content["content"]["user"]["name"]))
    return " ".join(content_array).replace("\n", "")


def create_video_block(video):
    if video["host"] == "youtube":
        return video["content"]["html"] + " <br><br>"
    elif video["host"] == "vimeo":
        return "<img src=" + video["imageURL"] + " height=" + str(video["imageHeight"]) \
               + " width=" + str(video["imageWidth"]) + " /> <br><br>"


def create_tweet_block(tweet):
    return '<strong>Tweet:</strong> "' + tweet["content"]["text"] + '" <br>' + "- " + tweet["content"]["user"]["name"] \
           + " (" + tweet["content"]["user"]["screen_name"] + ") <br><br>"


def parse_text(text):
    soup = BeautifulSoup(text, "html.parser")
    if twpc_options.mode == "html":
        return soup.text + " <br><br>"
    else:
        return soup.text


# Saves data as csv
def save_as_csv(data):
    df = pd.DataFrame(data)
    if os.path.exists(twpc_options.save_path):
        df.to_csv(twpc_options.save_path, sep=",", index=False, header=False, mode="a")
    else:
        df.to_csv(twpc_options.save_path, sep=",", index=False, header=True, mode="w")


# Class to set options used in the program
class TWPCOptions:
    def __init__(self, source_path, save_path, mode=None, batch_size=None, unwanted_properties=None):
        self.mode = mode if mode in ("html", "plain") else "plain"
        self.batch_size = 10000 if batch_size is None else batch_size
        self.unwanted_properties = ("source", "published_date") if unwanted_properties is None else unwanted_properties
        self.source_path = source_path
        self.save_path = save_path


if __name__ == "__main__":
    filterwarnings("ignore", category=UserWarning, module="bs4")  # Suppress userwarnings
    twpc_options = TWPCOptions(
        source_path="E:\\data\\TWPC.jl",
        save_path="E:\\data\\twp_corpus_html.csv",
        batch_size=10000,
        mode="html"
    )
    main()
