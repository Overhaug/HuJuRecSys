import common

FEATURE = "time"


def time_week_distance(sp, df):
    common.week_distance(sp, df, FEATURE)


def time_exp_decay(sp, df):
    common.exp_time_decay(sp, df)