from datetime import timedelta, date

import pandas as pd

from utils import get_df, get_id_path_pairs

years = (2012, 2013, 2014, 2015, 2016, 2017)


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


def sample_stratified_per_year(df, s, n):
    print(f"Sampling {n} articles per year in {years}'")
    final = pd.DataFrame()
    file_paths = get_id_path_pairs(df, save_path="E:\\data\\id_path.csv", from_path="drive")
    file_paths = list(file_paths.keys())
    for y in years:
        y_df = df.loc[df.date.dt.year == y]
        y_df = y_df[y_df.id.isin(file_paths)]
        sample = y_df.sample(n)
        final = pd.concat([final, sample])
    save_as_csv(final, s)
    print(f"Saved {len(final)} articles to {s}")


def save_as_csv(df, path):
    df.to_csv(path, sep=',', index=False, header=True, mode='w')


if __name__ == '__main__':
    main_file = 'E:\\data\\twp_corpus_html.csv'
    data = get_df(main_file, drop_nans=True, topic="Politics")
    sample_stratified_per_year(data, 'E:\\data\\stratified_politics_sample_html.csv', n=400)
