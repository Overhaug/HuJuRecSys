import calendar
import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import collections
import math

pd.set_option('display.max_colwidth', -1)
months = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}


def year_month_day_distribution(df, years, save=False):
    month_year_df = get_month_in_year_df(df, years)
    width = [3] * len(months)
    height = [2] * len(years)

    columns = len(months)
    rows = len(years)
    fig, ax_array = plt.subplots(rows, columns, squeeze=True, sharey='col',
                                 gridspec_kw={'width_ratios': width, 'height_ratios': height})
    n = 0
    for i, ax_row in enumerate(ax_array):
        for j, axes in enumerate(ax_row):
            if i == 5 and j > 7:
                axes.set_visible(False)
                continue
            data = month_year_df[n]
            last_day = int(data.day.max())
            mondays = get_first_monday(data)
            axes.set_xticks(np.arange(mondays, last_day, 7))
            axes.grid(axis='y', linewidth=0.3)
            axes.plot(data.day, data.counts)
            n += 1

    for ax, month in zip(ax_array[0], months):
        ax.set_title(months[month], size="20")

    for ax, year in zip(ax_array[:, 0], years):
        ax.set_ylabel(year, rotation=90, size="20")

    fig.text(0.10, 0.5, 'Year', ha='center', rotation=90, size="20")
    fig.text(0.5, 0.05, 'Month', ha='center', size="20")
    fig.text(0.65, 0.18, 'Note: x-axis on each subplot represent Mondays', size="14")
    plt.gcf().set_size_inches(50, 13)
    if save is True:
        plt.savefig('E:\\figs\\' + 'year_month_day_distribution' + '.png', bbox_inches='tight')
    plt.show()


def get_month_in_year_df(dates_df, years):
    month_year_df = []
    for year in years:
        year_df = dates_df.loc[dates_df.published_date.dt.year == int(year)]
        for m in year_df.published_date.dt.month.unique():
            month_df = year_df.loc[year_df.published_date.dt.month == m]
            current_month = pd.DataFrame()
            for d in month_df.published_date.dt.day.unique():
                c = len(month_df.loc[month_df.published_date.dt.day == d])
                current_month = pd.concat(
                    [current_month, pd.DataFrame({'year': [year], 'month': [m], 'day': [d], 'counts': [c]})]
                )
            current_month.sort_values(by=['month', 'day'], inplace=True)
            month_year_df.append(current_month)
    return month_year_df


def no_of_articles_per_year_for_a_month(dates_df, a_months, save=False):
    for month in a_months:
        month_df = dates_df.loc[dates_df.dt.month == int(month)]
        month_name = str(months[month])
        month_df.groupby([month_df.dt.year]).count().plot(kind="bar")
        plt.title("No. of news items per year for " + month_name)
        if save is True:
            plt.savefig('D:/newsRecSys/data/figs/' + 'articles_per_year_for_' + month_name + '.pdf')
        plt.show()
        plt.close()


def no_of_articles_per_year(dates_df, save=False):
    dates_df.groupby([dates_df.dt.year]).count().plot(kind="bar")
    plt.title("No. of news items per year (2012-2017)")
    if save is True:
        plt.savefig('D:/newsRecSys/data/figs/' + 'articles_per_year' + '.pdf')
    plt.show()
    plt.close()


def no_of_articles_per_month_all_years(dates_df, save=False):
    dates_df.groupby([dates_df.dt.month]).count().plot(kind="line")
    plt.title("Total no. of news items per month (2012-2017)")
    if save is True:
        plt.savefig('E:/figs/' + 'articles_per_month_all_years' + '.pdf')
    plt.show()
    plt.close()


def no_of_articles_per_day_overall(dates_df, save=False):
    plt.figure(figsize=(12, 8))
    for month in months:
        month_df = dates_df.loc[dates_df.published_date.dt.month == int(month)]
        month_df.groupby([month_df.published_date.dt.day]).count().plot(kind="line")
    plt.title("Total no. of news items per day (2012-2017)")
    plt.xticks(range(1, 32))
    plt.xlabel('Day')
    plt.ylabel('Articles')
    plt.legend([month for month in months.values()])
    if save is True:
        plt.savefig('D:/newsRecSys/data/figs/' + 'articles_per_day_all_years' + '.pdf')
    plt.show()
    plt.close()


def overall_distribution(dates_df, years, save=False):
    plt.figure(figsize=(12, 8))
    plt.title("Articles per month (2012-2017)")
    for year in years:
        year_df = dates_df.loc[dates_df['published_date'].dt.year == int(year)]
        year_df.groupby([year_df['published_date'].dt.month]).count().plot(kind='line')

    plt.legend([year for year in years])
    plt.xticks(range(1, 13))
    plt.grid()
    plt.xlabel('Month')
    plt.ylabel('Articles')
    if save is True:
        plt.savefig('D:/newsRecSys/data/figs/' + 'overall_distribution' + '.pdf')
    plt.show()
    plt.close()


def top_cat_month():
    plt.figure(figsize=(12, 8))
    f = get_df(source='D:\\newsRecSys\\data\\corpus_csv2.csv', dt=True)
    df = pd.DataFrame()
    for m in months:
        x = f.loc[f['published_date'].dt.month == int(m)]
        df = pd.concat([df, pd.DataFrame({'month': m, 'size': [x['topic'].count()]})])

    # f.groupby([f['published_date'].dt.month, f.topic])['topic'].count().plot(kind='bar', stacked=True)
    print(df)
    df.plot(x='month', y='size', kind='line')

    plt.xticks(range(1, 13))
    # plt.tick_params(
    #     axis='x',  # changes apply to the x-axis
    #     which='both',  # both major and minor ticks are affected
    #     bottom=False,  # ticks along the bottom edge are off
    #     top=False,  # ticks along the top edge are off
    #     labelbottom=False)  # labels along the bottom edge are off

    plt.show()
    plt.close()


def get_top_n_categories():
    # with_nans = get_df(source='D:\\newsRecSys\\data\\corpus_csv4.csv', dt=False, drop_nans=False)
    without_nans = get_df(source='D:\\newsRecSys\\data\\corpus_csv.csv', dt=False, drop_nans=True)
    categories = without_nans.category.unique()

    top_n = pd.DataFrame()
    for category in categories:
        topic_df = without_nans.loc[without_nans.category == category]
        top_n = pd.concat([top_n, pd.DataFrame({'category': [category], 'size': [int(len(topic_df))]})])

    # top_n = top_n_topics(topic_dist)
    # j = []
    # for c in top_n.itertuples():
    #    topic_df_nans = with_nans.loc[with_nans.category == c.category]
    #    j.append(len(topic_df_nans))

    # top_n['size_nans'] = j
    # save_as_csv(top_n, save_loc='D:\\newsRecSys\\data\\categories.csv')
    return top_n


def topic_distribution(df=False, save=False):
    df = get_df('D:\\newsRecSys\\data\\categories.csv')
    if df is False:
        df = get_top_n_categories()
    # plt.figure(figsize=(12, 8))
    width = 0.2
    df.sort_values(by=['size'], inplace=True, ascending=False)

    plt.rcParams.update({'font.size': 8})

    print(df)

    top_20 = df[:20]
    top_20['color'] = 'red'
    bottom = df[20:]
    bottom['color'] = 'blue'

    # bottom.rename(columns={'size': 'size_bottom'}, inplace=True)
    df2 = pd.concat([top_20, bottom], sort=False)

    df['size'].plot(kind='bar', color=df2.color, legend=None)
    # bottom['size_bottom'].plot(kind='bar', color=bottom.color, legend=None, ax=ax2)
    plt.xticks(np.arange(0, len(df.category), 1), labels=list(df.category))
    plt.yticks(np.arange(0, 77501, 2500))
    plt.gcf().set_size_inches(10, 7)

    plt.title("Category distribution in TREC Washington Post Corpus")
    plt.grid(axis='y', linewidth=0.3)
    plt.subplots_adjust(bottom=0.2)

    if save is True:
        plt.savefig('E:/figs/' + 'top_n_categories' + '.png')
    plt.show()
    plt.close()


def top_n_topics(distribution, n=10):
    distribution.sort_values(by=['size'], inplace=True)
    return distribution.tail(n)


def subtype(d):
    types = ('standalone', 'compilation')

    df = pd.DataFrame()
    for t in types:
        t_df = d.loc[d.subtype == t]
        df = pd.concat([df, pd.DataFrame({'subtype': [t], 'size': [len(t_df)]})])

    print(df)


def get_df(source, only_dates=False, drop_nans=True, dt=True):
    df = pd.read_csv(source)
    if only_dates is True:
        return pd.DataFrame(
            {'published_date': pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')})
    if dt is True:
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        df['time'] = pd.to_datetime(df['time'], format='%H-%M-%S', errors='coerce')
    if drop_nans is True:
        df.dropna(inplace=True)
    return df


def save_as_csv(data, save_loc):
    data.to_csv(save_loc, sep=',', index=False, header=True, mode='w')


def get_first_monday(dates):
    for i, day in dates.iterrows():
        date = str(str(day['year']) + '-' + str(day['month']) + '-' + str(day['day']))
        d = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()
        dayname = calendar.day_name[d]
        if dayname == 'Monday':
            return int(day['day'])


def tf_idf(data):
    pol = data.loc[data['category'] == 'Politics']
    tfidfs = pd.DataFrame()

    stemmer = SnowballStemmer("english")
    stop = stopwords.words("english")

    for y in (2016, 2017):
        data_in_year = pol.loc[pol['published_date'].dt.year == y]
        #print(len(d), y)

        idf = math.log(len(data_in_year) / len(data_in_year[data_in_year['text'].str.lower().apply(lambda x: 'election' in x)]))

        data_in_year['split_text'] = data_in_year['text'].str.split()

        data_in_year['stemmed'] = data_in_year['split_text'].apply(lambda x: [stemmer.stem(j) for j in x])
        data_in_year['resulting_text'] = data_in_year['stemmed'].apply(lambda x: [word for word in x if word not in stop])
        #print(len(t), y)

        #print(len(d) / len(t), 'idf', '\n')
        ct = 0

        tfidf = []
        for i, row in data_in_year.iterrows():
            text = row['resulting_text'] #str(row['resulting_text']).lower()
            tf = text.count('election') / len(text)
            # most = []
            # for t in text.split():
            #     tcc = text.split().count(t) / len(text.split())
            #     most.append((t, tcc))
            counter = collections.Counter(text)
            most_common = counter.most_common()[0]
            if most_common[0] == 'election':
                ct += 1
            try:
                tfidf.append(tf * idf)
            except ZeroDivisionError:
                pass
        print(ct, y)
        avg_tfidf = sum(tfidf) / len(tfidf)
        tfidfs = pd.concat([tfidfs, pd.DataFrame({'year': y, 'tf-idf': [avg_tfidf]})])
        print("{:.2%}".format(avg_tfidf), avg_tfidf)

    tfidfs.plot()
    plt.show()


def avg_article_length(data):
    df = pd.DataFrame()

    for y in (2012, 2013, 2014, 2015, 2016, 2017):
        data_in_year = data.loc[data['date'].dt.year == y]
        df_year = pd.DataFrame()
        for m in months:
            lm = []
            data_in_month = data_in_year.loc[data_in_year['date'].dt.month == m]
            for i, row in data_in_month.iterrows():
                lm.append(len(row['text'].split()))
            try:
                df_year = pd.concat([df_year, pd.DataFrame({
                    'year': [y], 'month': [m], 'avg_length': [sum(lm) // len(lm)]
                })])
            except ZeroDivisionError:
                pass
        df = pd.concat([df, df_year])

    df = pd.concat([df, avg_article_length_per_month_across_all_years(df)])
    print(df)
    df = df.pivot(index='month', columns='year', values='avg_length')
    df.plot()

    plt.legend()
    plt.xticks(np.arange(1, 13))
    plt.ylabel('Article length')
    plt.show()


def avg_article_length_per_month_across_all_years(data):
    df = pd.DataFrame()
    for m in months:
        mo = data.loc[data['month'] == m]
        df = pd.concat([df, pd.DataFrame({
            'year': 'all years', 'month': [m], 'avg_length': [sum(mo['avg_length']) // len(mo)]
        })])
    return df



if __name__ == '__main__':
    mainfile = 'D:\\newsRecSys\\data\\corpus2.csv'
    f = get_df(source=mainfile)
    # save_as_csv(f, save_loc="E:/data/dates.csv")
    # no_of_articles_per_month_for_a_year(dates, (2011, 2012, 2013, 2014, 2015, 2016, 2017))
    # no_of_articles_per_year_for_a_month(dates, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
    # no_of_articles_per_year(dates)
    # no_of_articles_per_month_all_years(dates)
    # overall_distribution(f, (2011, 2012, 2013, 2014, 2015, 2016, 2017))
    # no_of_articles_per_day_overall(dates)
    # top_cat_month()
    # topic_distribution(df=True, save=True)
    # no_of_articles_per_month_all_years(f)
    years = (2012, 2013, 2014, 2015, 2016, 2017)
    # year_month_day_distribution(f, years=years, save=True)
    # tf_idf(f)
    avg_article_length(f)
    # top_n = get_df('D:\\newsRecSys\\data\\categories.csv')
    # top_n.sort_values(by=['size'], inplace=True, ascending=False)
    # save_as_csv(top_n, save_loc='D:\\newsRecSys\\data\\categories.csv')
