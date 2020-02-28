#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A utility class for twpc.py
"""
from bs4 import BeautifulSoup


class TWPCHelper:
    def __init__(self, source_path, save_path, mode=None, batch_size=None, properties_to_discard=None):
        self.mode = mode if mode in ("html", "plain") else "plain"
        self.batch_size = 10000 if batch_size is None else batch_size
        self.properties_to_discard = ("source", "published_date") if properties_to_discard is None \
            else properties_to_discard
        self.source_path = source_path
        self.save_path = save_path + "_" + self.mode + ".csv" if not save_path.endswith(".csv") else save_path
        self.parser = self.get_parser()
        self.print()

    def get_parser(self):
        if self.mode == 'html':
            return self.parse_as_html
        if self.mode == 'plain':
            return self.parse_as_plain

    @staticmethod
    def parse_as_html(text):
        soup = BeautifulSoup(text, "html.parser")
        if soup.text.isspace() or soup.text == '':
            return ''
        return soup.text + " <br><br>"

    @staticmethod
    def parse_as_plain(text):
        soup = BeautifulSoup(text, "html.parser")
        if soup.text.isspace() or soup.text == '':
            return ''
        return soup.text

    def print(self):
        attrs = vars(self)
        print(f"This run is defined by the following attributes:")
        print('\n'.join("%s: %s" % item for item in attrs.items()))
