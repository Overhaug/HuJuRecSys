import pandas as pd
from datetime import timedelta, date

years = (2012, 2013, 2014, 2015, 2016, 2017)


def df_with_dt(f):
    df = pd.read_csv(f).dropna()
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    df['time'] = pd.to_datetime(df['time'], format='%H-%M-%S', errors='coerce')
    return df


def sample_frac_per_day(df, frac=10):
    def date_range(start, end):
        for n in range(int((end - start).days)):
            yield start + timedelta(n)

    min_date = pd.Timestamp(min(df['date']))
    max_date = pd.Timestamp(max(df['date']))

    start_date = date(min_date.year, min_date.month, min_date.day)
    end_date = date(max_date.year, max_date.month, max_date.day)

    new_df = pd.DataFrame()

    for a_date in date_range(start_date, end_date):
        articles_in_date = df.loc[df['date'] == pd.Timestamp(a_date)]
        try:
            sample = articles_in_date.sample(frac)
            new_df = pd.concat([new_df, sample])
        except ValueError:  # Number of items in article_in_date is less than sample size
            new_df = pd.concat([new_df, articles_in_date])

    save_as_csv(new_df, 'D:/newsRecSys/data/sample.csv')


def sample_stratified_per_year(df, s, n, topic=None):
    final = pd.DataFrame()
    if topic is not None:
        df = df.loc[df.category == topic]
    for y in years:
        sample = df.loc[df.date.dt.year == y].sample(n)
        final = pd.concat([final, sample])
    save_as_csv(final, s)


def save_as_csv(data, path):
    data.to_csv(path, sep=',', index=False, header=True, mode='w')


mainfile = 'E:\\data\\corpus_wo_breaklines.csv'
data = df_with_dt(mainfile)
sample_stratified_per_year(data, 'E:\\data\\stratified_sample.csv', n=340)
