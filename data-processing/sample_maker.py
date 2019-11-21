import pandas as pd
from datetime import timedelta, date


def df_with_dt():
    df = pd.read_csv('D:/newsRecSys/data/corpus_csv.csv').dropna()
    df['published_date'] = pd.to_datetime(df['published_date'], format='%Y-%m-%d', errors='coerce')
    return df


def even_extraction(df, sample_size=10):
    def date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    min_date = pd.Timestamp(min(df['published_date']))
    max_date = pd.Timestamp(max(df['published_date']))

    start_date = date(min_date.year, min_date.month, min_date.day)
    end_date = date(max_date.year, max_date.month, max_date.day)

    new_df = pd.DataFrame()

    for a_date in date_range(start_date, end_date):
        articles_in_date = df.loc[df['published_date'] == pd.Timestamp(a_date)]
        try:
            sample = articles_in_date.sample(sample_size)
            new_df = pd.concat([new_df, sample])
        except ValueError:  # Number of items in article_in_date is less than sample size
            new_df = pd.concat([new_df, articles_in_date])

    save_as_csv(new_df, 'D:/newsRecSys/data/sample.csv')


def save_as_csv(data, path):
    data.to_csv(path, sep=',', index=False, header=True, mode='w')


if __name__ == '__main__':
    data = df_with_dt()
    even_extraction(data, sample_size=30)