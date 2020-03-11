#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A module that creates (most of) the necessary files in order to compute similarities.
    Just an easier way to create the improved .CSV version of the TWPC and a sample set.
"""
import os
from datetime import datetime

import definitions
import sampler
import utils
from twpc import twpc_articles
from twpc_helper import TWPCHelper


class Process:
    """
        :param which defines if the session should create all files necessary,
        only from sample (given a main file exists), or to only create the main file.
        :param category defines which category to sample from
        :param drop_nans defines whether to ignore articles which missing values
        :param drop_duplicates defines whether to ignore articles
        where the main text of an article has already been seen.
    """
    valid_scopes = ("mainfile", "sample", "both")

    def __init__(self, which="all", base_dir=None, source_path=None, main_path=None,
                 category=None, drop_nans=None, drop_duplicates=None, n=None):
        self.paths = definitions.get_paths()
        self.which = which.lower()
        self.category = category
        self.drop_nans = drop_nans
        self.drop_duplicates = drop_duplicates
        self.n = n
        self.base_dir = base_dir if base_dir is not None and base_dir.endswith("/") else self.paths["basedir"]
        self.source_path = source_path if source_path is not None else self.paths["corpusdir"]
        self.session_path = self.__create_session_directory()
        self.paths["sessionpath"] = self.session_path
        self.main_path = main_path if main_path is not None else self.paths["sessionpath"]\
                                                                 + "twpc-" + self.which + ".csv"
        self.__validate_args()
        self.sample_path = self.session_path + "sample_" + self.category + "_" + str(self.n) + ".csv"
        self.sample_file = None
        self.main_file = None
        self.run()

    def __validate_args(self):
        if self.which not in self.valid_scopes:
            raise ValueError(f"Valid which arguments are {self.valid_scopes}")
        if self.which == "sample" or self.which == "both":
            args = [self.category, self.drop_nans, self.drop_duplicates, self.n, self.main_path]
            if all(args) is False:
                raise ValueError(f"When arg which is set to 'sample' or 'all-sample', args {args} must be passed")
        if self.which == "sample":
            if not os.path.exists(self.main_path):
                raise OSError(f"File {self.main_path} does not exist!")
        if not os.path.isdir(self.base_dir):
            raise OSError(f"{self.base_dir} is not a directory!")
        if self.which in ("both", "mainfile") and not os.path.exists(self.source_path):
            raise OSError(f"{self.source_path} is not a directory!")

    def __create_session_directory(self):
        timestamp = datetime.now()
        ts_string = timestamp.strftime("%d-%m-%Y-%H-%M")
        os.mkdir(self.paths["datadir"] + ts_string)
        return self.base_dir + ts_string + "/"

    def run(self):
        if self.which == "mainfile":
            self.__mainfile()
        elif self.which == "all-sample":
            self.__mainfile()
            self.__sample()
        else:
            self.__sample()

    def __mainfile(self):
        twpc_helper = TWPCHelper(
            source_path=self.paths["datadir"] + "corpus/TWPC.jl",
            save_path=self.session_path + "twpc_corpus_html.csv"
        )
        this = twpc_articles.TWPC(twpc_helper)
        this.run()

    def __sample(self):
        self.main_file = utils.get_df(self.main_path, drop_nans=self.drop_nans,
                                      drop_duplicates=self.drop_duplicates, category=self.category)
        sampler.sample_stratified_per_year(
            df=self.main_file, s=self.sample_path, n=self.n)


if __name__ == '__main__':
    proc = Process(which="mainfile", drop_nans=True,
                   drop_duplicates=True, category="Politics", n=400)
