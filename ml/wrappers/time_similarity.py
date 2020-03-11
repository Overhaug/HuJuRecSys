import common

FEATURE = "time"


def time_week_distance(sp, df, db):
    common.week_distance(sp, df, FEATURE, db)


def time_exp_decay(sp, df, db):
    common.exp_time_decay(sp, df, FEATURE, db)