import common

FEATURE = "text"


def text_tfidf_cosine_sim(sp, df, db):
    vectors = common.tfidf(df, FEATURE)
    common.cosine_similarity(sp, df, vectors, db)

# TODO: LDA
