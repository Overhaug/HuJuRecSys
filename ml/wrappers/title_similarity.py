import common
import lda

FEATURE = "title"


def title_jw(sp, df):
    common.jaro_winkler(sp, df, FEATURE)


def title_levenshtein(sp, df):
    common.levenshtein(sp, df, FEATURE)


def title_lcs(sp, df):
    common.longest_common_subsequence(sp, df, FEATURE)


def title_ngram(sp, df, n):
    common.n_gram(sp, df, FEATURE, n)


def title_lda(sp, df, session, update_model):
    lda.cs_lda(sp, df, FEATURE, session, update_model)
