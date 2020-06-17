## Developing and Comparing Similarity Functions for the News Recommender Domain Using Human Judgements
### Master's Thesis
#### Contents
* Scripts for processing the 2017-version of the Wasington Post Corpus, provided by TREC (https://trec.nist.gov/data/wapost/)
* Scripts for downloading embedded images
* Various methods for computing similarity on a number of article properties. Can be viewed in (sim -> similarity_functions.py)
* Various methods for creating graphs of the resulting dataset/sample, e.g. graphs of date of publication distributions
* Methods for sampling using a multi-stage approach, where articles with nan's are ignored, identifies articles with corrupted images, and more
- Various methods for processing images, i.e. checking for corrupted images using multiprocessing. Takes about 10 minutes with 650K images on an SSD.

And many more, small methods to help exploring the dataset.

#### PS: definitions.py in the root folder should be modified to a user's needs. This defines the folders from which functions attempts to find files/folders that have been created in an earlier process. For instance, when computing similarity, definitions.py is used to automatically fetch the destination folder for similarity scores, which is defined by the root of the "data" key. Thus, the root folder in definitions.py must be changed!
