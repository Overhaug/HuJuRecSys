# Master thesis repo . . .
## Contents
* Scripts for processing TREC Washington Post Corpus (done/in-progress)
  * Script for cleaning dataset and converting to .csv format.
    * nan's for empty values, flattens nested json-structure, cleans html tags, ...
  * Script for:
    * Downloading all images by using multithreaded requests (grequests)
    * Extracting all image urls available across all articles, store them as id-url pairs in a .csv file.
* Machine learning models to compute similarity of news articles (to-do)
