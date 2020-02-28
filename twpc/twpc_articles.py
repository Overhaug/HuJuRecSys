#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A script to clean and improve the TREC Washington Post Corpus for use in research. Creates a CSV file.
"""
import os
import re
from datetime import datetime as dt
from warnings import filterwarnings

import pandas as pd
import pytz
from json_lines import reader as jl_reader

import categories
from twpc_helper import TWPCHelper
from utils import options, file_len, rindex


class TWPC:
    filterwarnings("ignore", category=UserWarning, module="bs4")  # Suppress userwarnings

    def __init__(self, twpc_helper):
        if isinstance(twpc_helper, TWPCHelper):
            self.twpc_helper = twpc_helper
        else:
            raise TypeError(f"The argument of TWPC must be an instance of TWPCHelper")

    def run(self):
        if os.path.exists(self.twpc_helper.save_path):
            self.twpc_helper.save_path = options(self.twpc_helper.save_path)
            print(f"New path: {self.twpc_helper.save_path}")
        articles = []
        end = file_len(self.twpc_helper.source_path)
        with open(self.twpc_helper.source_path, "rb") as f:
            for i, article in enumerate(jl_reader(f), start=1):
                article["contents"] = list(filter(None, article["contents"]))
                article["text"] = self.stringify_contents(article)
                article["date"], article["time"] = self.unix_to_dt(article)
                article["image_url"], article["image_caption"] = self.get_image_url_and_caption(article)
                article["author_bio"] = self.get_author_bio(article)
                article["category"], article["subcategory"] = self.get_categories(article)
                if article["title"] is None or article["title"] == "":
                    article["title"] = "NaN"
                if article["author"] == "":
                    article["author"], article['subtype'] = self.get_author_if_compilation(article)
                else:
                    article["subtype"] = "standalone"
                self.discard_properties(article)
                articles.append(article)
                if i % self.twpc_helper.batch_size == 0 or i == end:
                    self.save_as_csv(articles)
                    articles = []
                    print(f"Progress: {i} / {end}.")

    def discard_properties(self, article):
        for prop in self.twpc_helper.properties_to_discard:
            del article[prop]
        del article["contents"]

    # Finds the appropriate main category group and returns this
    @staticmethod
    def get_categories(article):
        for content in article["contents"]:
            if content["type"] == "kicker" \
                    and "content" in content and content["content"] is not None:
                return categories.get_group(content["content"]), content["content"]
        return "NaN", "NaN"

    # Gets author bio from content array
    def get_author_bio(self, article):
        for content in article["contents"]:
            if "bio" in content and content["bio"] != "":
                return self.twpc_helper.parser(content["bio"])
        return "NaN"

    @staticmethod
    def is_compilation(article):
        for content in article["contents"]:
            if "content" in content and str(content["content"]).__contains__("Compiled by"):
                return content["content"]
        return False

    # Gets author if not present in article
    def get_author_if_compilation(self, article):
        compilation = self.is_compilation(article)
        if compilation is not False:
            clean = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
            clean_text = str(re.sub(clean, "", compilation)).split()
            i = rindex(clean_text, "by")
            return " ".join(clean_text[i + 1:]), "compilation"
        return "NaN", "standalone"

    # Assumes that the first content-blob found with a fullcaption and image URL is the "main" image of the article/blog
    def get_image_url_and_caption(self, article):
        for content in article["contents"]:
            if content["type"] == "image":
                if "fullcaption" in content and content["fullcaption"] != "" and content["imageURL"] != "":
                    return content["imageURL"], self.twpc_helper.parser(content["fullcaption"])
        return "NaN", "NaN"

    # Convert unix dates to datetime string
    @staticmethod
    def unix_to_dt(article):
        try:
            article["date"] = dt.utcfromtimestamp(article["published_date"] / 1000.0) \
                .astimezone(pytz.timezone("America/New_York"))
            article["time"] = article["date"].time().strftime("%H:%M:%S")
            article["date"] = article["date"].date().strftime("%Y-%m-%d")
            return article["date"], article["time"]
        except TypeError:
            print(f"Unable to convert {article['published_date']}, for id: {article['id']}")
            return "NaN", "NaN"
        except OSError:
            print(f"Invalid argument: {article['published_date']}, for id: {article['id']}")
            return "NaN", "NaN"

    # Finds relevant content in the contents-array found in articles
    def stringify_contents(self, article):
        content_array = []
        for content in article["contents"]:
            if content["type"] == "sanitized_html":
                # Some articles have manually inserted "Read more" sections, which we do not want
                if str(content['content']).lower().__contains__("read more"):
                    break  # We assume that if the object matches the condition, we are at the end of the article
                content_array.append(self.twpc_helper.parser(content["content"]))
            elif content["type"] == "list":
                for item in content["content"]:
                    content_array.append(self.twpc_helper.parser(item))
            elif self.twpc_helper.mode == "html":
                if content["type"] == "video" and "content" in content:
                    content_array.append(self.create_video_block(content))
                elif content["type"] == "tweet":
                    content_array.append(self.create_tweet_block(content))
            elif content["type"] == "tweet":
                content_array.append(self.twpc_helper.parser(content["content"]["text"]))
                content_array.append(self.twpc_helper.parser(content["content"]["user"]["name"]))
        content_array = list(filter(None, content_array))  # Remove empty strings
        final_string = " ".join(content_array).replace("\n", "")
        if final_string == "":
            final_string = "NaN"
        return final_string

    @staticmethod
    def create_video_block(video):
        if video["host"] == "youtube":
            return video["content"]["html"] + " <br><br>"
        elif video["host"] in ("vimeo", "posttv"):
            return "<img src=" + video["imageURL"] + " height=" + str(video["imageHeight"]) \
                   + " width=" + str(video["imageWidth"]) + " /> <br><br>"

    @staticmethod
    def create_tweet_block(tweet):
        return '<strong>Tweet:</strong> "' + tweet["content"]["text"] + '" <br>' + "- " + \
               tweet["content"]["user"]["name"] + " (" + tweet["content"]["user"]["screen_name"] + ") <br><br>"

    # Saves data as csv
    def save_as_csv(self, data):
        df = pd.DataFrame(data)
        if os.path.exists(self.twpc_helper.save_path):
            df.to_csv(self.twpc_helper.save_path, sep=",", index=False, header=False, mode="a")
        else:
            df.to_csv(self.twpc_helper.save_path, sep=",", index=False, header=True, mode="w")
