import common

FEATURE = "title"


def title_jw(sp, df, db):
    common.jaro_winkler(sp, df, FEATURE, db)


def title_levenshtein(sp, df, db):
    common.levenshtein(sp, df, FEATURE, db)


def title_lcs(sp, df, db):
    common.longest_common_subsequence(sp, df, FEATURE, db)

# TODO: Bigram, LDA
