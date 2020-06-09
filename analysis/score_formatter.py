"""
A hacky way to reformat pivot-style csv files to standard table-style. Unnecessary, but simplifies other aspects later
"""

import pandas as pd

import metric_combiner
import utils


def format_score():
    def do(name, data):
        formatted_scores = pd.DataFrame(columns=["first", "second", "score"])
        ids = data.columns
        scores_length = len(data)
        for i, column in enumerate(data.columns.values):
            temp = pd.DataFrame()
            temp["first"] = [column for _ in range(scores_length)]
            temp["second"] = ids
            temp["score"] = data[column].values
            formatted_scores = pd.concat([formatted_scores, temp])
        formatted_scores.dropna(inplace=True)
        formatted_scores.to_csv("E:/data/Final/formatted/" + name, index=False)

    sims = [metric_combiner.all_category(), metric_combiner.all_title(), metric_combiner.all_image(),
            metric_combiner.all_author(), metric_combiner.all_time(), metric_combiner.all_text(),
            metric_combiner.all_authorbio()]

    for s in sims:
        for k, v in s.items():
            print(f"Formatting {k}")
            do(k, v)


def combine():
    # The index of title_lev is used as template for  the rest
    title_lev = utils.get_df("E:/data/Final/formatted/" + "title-levenshtein.csv") \
        .rename(columns={"score": "title_lev"})

    title_jw = utils.get_df("E:/data/Final/formatted/" + "title-jarowinkler.csv") \
        .rename(columns={"score": "title_jw"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    title_lcs = utils.get_df("E:/data/Final/formatted/" + "title-lcs.csv") \
        .rename(columns={"score": "title_lcs"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    title_bigram = utils.get_df("E:/data/Final/formatted/" + "title-ngram.csv") \
        .rename(columns={"score": "title_bigram"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    title_lda = utils.get_df("E:/data/Final/formatted/" + "title-lda.csv") \
        .rename(columns={"score": "title_lda"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    text_sent = utils.get_df("E:/data/Final/formatted/" + "text-sentiment-sim.csv") \
        .rename(columns={"score": "text_sent"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    text_lda = utils.get_df("E:/data/Final/formatted/" + "text-lda.csv") \
        .rename(columns={"score": "text_lda"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    text_tfidf = utils.get_df("E:/data/Final/formatted/" + "text-tfidf-cs.csv") \
        .rename(columns={"score": "text_tfidf"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    text50_tfidf = utils.get_df("E:/data/Final/formatted/" + "text-tfidf-cs-constr.csv") \
        .rename(columns={"score": "text50_tfidf"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    sharpness = utils.get_df("E:/data/Final/formatted/" + "sharpness-sim.csv") \
        .rename(columns={"score": "sharpness"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    entropy = utils.get_df("E:/data/Final/formatted/" + "entropy-sim.csv") \
        .rename(columns={"score": "entropy"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    brightness = utils.get_df("E:/data/Final/formatted/" + "brightness-sim.csv") \
        .rename(columns={"score": "brightness"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    colorfulness = utils.get_df("E:/data/Final/formatted/" + "colorfulness-sim.csv") \
        .rename(columns={"score": "colorfulness"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    embeddings = utils.get_df("E:/data/Final/formatted/" + "embeddings-cs.csv") \
        .rename(columns={"score": "embeddings"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    contrast = utils.get_df("E:/data/Final/formatted/" + "contrast-sim.csv") \
        .rename(columns={"score": "contrast"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    bio_tfidf = utils.get_df("E:/data/Final/formatted/" + "bio-tfidf-cs.csv") \
        .rename(columns={"score": "bio_tfidf"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    bio_lda = utils.get_df("E:/data/Final/formatted/" + "bio-lda.csv") \
        .rename(columns={"score": "bio_lda"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    author_jacc = utils.get_df("E:/data/Final/formatted/" + "author-jaccard.csv") \
        .rename(columns={"score": "author_jacc"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    daydist = utils.get_df("E:/data/Final/formatted/" + "days-distance-similarity.csv") \
        .rename(columns={"score": "daydist"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)
    subcat_jacc = utils.get_df("E:/data/Final/formatted/" + "category-jaccard.csv") \
        .rename(columns={"score": "subcat_jacc"}).set_index("first") \
        .reindex(index=title_lev["first"]).reset_index().drop(["first", "second"], axis=1)

    data = pd.concat([title_lev, title_jw, title_lcs, title_bigram, title_lda, text_sent, text_lda,
                      text_tfidf, text50_tfidf, sharpness, entropy, brightness, colorfulness, embeddings,
                      contrast, bio_tfidf, bio_lda, author_jacc, daydist, subcat_jacc], axis=1)
    data.to_csv("E:/data/Final/formatted/all_scores.csv", index=False)


combine()
