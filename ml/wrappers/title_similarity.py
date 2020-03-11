import common
import lda

FEATURE = "title"


def title_jw(sp, df, db):
    common.jaro_winkler(sp, df, FEATURE, db)


def title_levenshtein(sp, df, db):
    common.levenshtein(sp, df, FEATURE, db)


def title_lcs(sp, df, db):
    common.longest_common_subsequence(sp, df, FEATURE, db)


def title_ngram(sp, df, db, n):
    common.n_gram(sp, df, FEATURE, db, n)


def title_lda(sp, df, db, session, update_model):
    lda.cs_lda(sp, df, FEATURE, db, session, update_model)
