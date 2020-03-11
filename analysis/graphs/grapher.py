#!/usr/bin/env python

import calendar
import datetime

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from twpc.utils import get_df

pd.set_option('display.max_colwidth', None)
months = {
    1: ['January', 'Jan'], 2: ['February', 'Feb'], 3: ['March', 'Mar'], 4: ['April', 'Apr'], 5: ['May', 'May'],
    6: ['June', 'June'],
    7: ['July', 'July'], 8: ['August', 'Aug'], 9: ['September', 'Sept'], 10: ['October', 'Oct'],
    11: ['November', 'Nov'], 12: ['December', 'Dec']
}


def year_month_day_distribution(df, title):
    month_year = get_month_in_year(df)
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
            data = month_year[n]
            last_day = int(data.day.max()) + 1
            try:
                mondays = get_first_monday(data)
                axes.set_xticks(np.arange(mondays, last_day, 7))
            except TypeError:
                pass  # No Mondays in the current month
            axes.grid(axis='y', linewidth=0.3)
            axes.plot(data.day, data.counts)  # todo: Change to max ytick of 1000
            n += 1

    for ax, month in zip(ax_array[0], months):
        m = months[month]
        ax.set_title(m[0], size="20")

    for ax, year in zip(ax_array[:, 0], years):
        ax.set_ylabel(year, rotation=90, size="20")

    fig.text(0.10, 0.5, 'Year', ha='center', rotation=90, size="20")
    fig.text(0.5, 0.05, 'Month', ha='center', size="20")
    fig.text(0.65, 0.18, 'Note: x-axis on each subplot represent Mondays', size="14")
    plt.gcf().set_size_inches(50, 13)
    title = '_'.join(title.split())
    plt.savefig('E:\\figs\\' + title + '.png', bbox_inches='tight')
    plt.show()


def get_month_in_year(dates_df):
    month_year_df = []
    for year in years:
        year_df = dates_df.loc[dates_df.date.dt.year == int(year)]
        for m in year_df.date.dt.month.unique():
            month_df = year_df.loc[year_df.date.dt.month == m]
            current_month = pd.DataFrame()
            for day in month_df.date.dt.day.unique():
                c = len(month_df.loc[month_df.date.dt.day == day])
                current_month = pd.concat(
                    [current_month, pd.DataFrame({'year': [year], 'month': [m], 'day': [day], 'counts': [c]})]
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
    dates_df.groupby([dates_df.dt.month]).count().plot(kind="bar")
    plt.title("Total no. of news items per month (2012-2017)")
    if save is True:
        plt.savefig('D:/newsRecSys/data/figs/' + 'articles_per_month_all_years' + '.pdf')
    plt.show()
    plt.close()


def no_of_articles_per_day_overall(dates_df, save=False):
    plt.figure(figsize=(12, 8))
    for month in months:
        month_df = dates_df.loc[dates_df.dt.month == int(month)]
        month_df.groupby([month_df.dt.day]).count().plot(kind="line")
    plt.title("Total no. of news items per day (2012-2017)")
    plt.xticks(range(1, 32))
    plt.xlabel('Day')
    plt.ylabel('Articles')
    plt.legend([month for month in months.values()])
    if save is True:
        plt.savefig('D:/newsRecSys/data/figs/' + 'articles_per_day_all_years' + '.pdf')
    plt.show()
    plt.close()


def overall_distribution(dates_df, save=False):
    plt.figure(figsize=(12, 8))
    plt.title("Articles per month (2012-2017)")
    for year in years:
        year_df = dates_df.loc[dates_df.dt.year == int(year)]
        year_df.groupby([year_df.dt.month]).count().plot(kind='line')

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
    f = get_df(source='D:\\newsRecSys\\data\\corpus_csv2.csv', drop_nans=True)
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


def get_top_n_categories(stacked):
    without_nans = get_df(source=mainfile, dt=False, drop_nans=True)
    categories = without_nans.category.unique()
    top_n_nans = pd.DataFrame()

    if stacked:
        with_nans = get_df(source=mainfile, dt=False, drop_nans=False)
        with_nans.replace(np.nan, 'N/A', regex=True, inplace=True)
        for category in categories:
            topic_df = with_nans.loc[with_nans.category == category]
            top_n_nans = pd.concat([top_n_nans, pd.DataFrame({'category': [category], 'size': [int(len(topic_df))]})])

    top_n = pd.DataFrame()
    for category in categories:
        topic_df = without_nans.loc[without_nans.category == category]
        top_n = pd.concat([top_n, pd.DataFrame({'category': [category], 'size': [int(len(topic_df))]})])

    if stacked:
        # cats = []
        # topcats = top_n['category'].tolist()
        # nancats = top_n_nans['category'].tolist()
        # print(len(topcats), len(nancats))
        # for x in nancats:
        #     if x not in topcats:
        #         cats.append(x)
        # n = [0 for x in cats]
        # print(cats, n)
        # top_n = pd.concat([top_n, pd.DataFrame({'category': cats, 'size': n})])

        return top_n_nans, top_n
    else:
        return top_n


def topic_distribution(save=False):
    df = get_top_n_categories(stacked=False)
    df.sort_values(by=['size'], inplace=True, ascending=False)

    plt.rcParams.update({'font.size': 8})

    top_20 = df[:20]
    top_20['color'] = 'red'
    bottom = df[20:]
    bottom['color'] = 'blue'

    # bottom.rename(columns={'size': 'size_bottom'}, inplace=True)
    df2 = pd.concat([top_20, bottom], sort=False)

    df['size'].plot(kind='bar', color=df2.color)
    # bottom['size_bottom'].plot(kind='bar', color=bottom.color, legend=None, ax=ax2)
    plt.xticks(np.arange(0, len(df.category), 1), labels=list(df.category))
    plt.yticks(np.arange(0, 80001, 2500))
    plt.ylabel("No. of articles")
    plt.gcf().set_size_inches(10, 7)
    red_patch = mpatches.Patch(color='red', label='Top 20')
    blue_patch = mpatches.Patch(color='blue', label='Bottom 20')
    plt.legend(handles=[red_patch, blue_patch])

    plt.title("Category distribution in TREC Washington Post Corpus")
    plt.grid(axis='y', linewidth=0.3)
    plt.subplots_adjust(bottom=0.2)

    if save is True:
        plt.savefig('E:/figs/' + 'top_n_categories' + '.png')
    plt.show()
    plt.close()


def topic_distribution_stacked_all(save=False):
    df, df2 = get_top_n_categories(stacked=True)
    plt.rcParams.update({'font.size': 8})

    df.sort_values(by=['size'], inplace=True, ascending=False)

    df2 = df2.set_index('category')
    df2 = df2.reindex(index=df['category'])
    df2 = df2.reset_index()
    # df2.sort_values(by=df['category'].tolist(), inplace=True)

    n = len(df.category)
    ind = np.arange(n)

    p1 = plt.bar(ind, df['size'])
    p2 = plt.bar(ind, df2['size'])
    plt.ylabel("No. of articles")
    plt.xticks(ind, list(df.category), rotation=90)
    plt.yticks(np.arange(0, 140001, 5000))
    plt.gcf().set_size_inches(10, 7)

    plt.title("Category distribution in TREC Washington Post Corpus")
    plt.grid(axis='y', linewidth=0.3)
    plt.subplots_adjust(bottom=0.25)
    plt.legend((p1[0], p2[0]), ('With NaNs', 'Without NaNs'))
    plt.margins(x=0)
    if save is True:
        plt.savefig('E:/figs/' + 'categories_stack_graph_alt' + '.png')
    plt.show()
    plt.close()


def top_n_topics(distribution, n=10):
    distribution.sort_values(by=['size'], inplace=True)
    return distribution.tail(n)


def subtype(data):
    types = ('standalone', 'compilation')

    df = pd.DataFrame()
    for t in types:
        t_df = data.loc[data.subtype == t]
        df = pd.concat([df, pd.DataFrame({'subtype': [t], 'size': [len(t_df)]})])

    print(df)


def save_as_csv(data, save_loc):
    data.to_csv(save_loc, sep=',', index=False, header=True, mode='w')


def get_first_monday(dates):
    for i, day in dates.iterrows():
        date = str(str(day['year']) + '-' + str(day['month']) + '-' + str(day['day']))
        a_day = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()
        dayname = calendar.day_name[a_day]
        if dayname == 'Monday':
            return int(day['day'])


def avg_article_length(df, process=False, title=None):
    if process:
        temp_df = pd.DataFrame()
        for y in (2012, 2013, 2014, 2015, 2016, 2017):
            data_in_year = df.loc[df['date'].dt.year == y]
            df_year = pd.DataFrame()
            for m in months:
                lm = []
                data_in_month = data_in_year.loc[data_in_year['date'].dt.month == m]
                for i, row in data_in_month.iterrows():
                    lm.append(len(row['title'].split()))
                try:
                    df_year = pd.concat([df_year, pd.DataFrame({
                        'year': [y], 'month': [m], 'avg_length': [sum(lm) // len(lm)]
                    })])
                except ZeroDivisionError:
                    pass
            temp_df = pd.concat([temp_df, df_year])
        df = pd.concat([temp_df, avg_article_length_per_month_all_years(temp_df)])
        path = '_'.join(title.split())
        save_as_csv(data=df, save_loc="E:\\data\\" + path + ".csv")

    each_year = df[df.year != 'all years']
    each_year = each_year.pivot(index='month', columns='year', values='avg_length')
    all_years_mean = df.loc[df.year == 'all years'].mean()
    m = [(all_years_mean['avg_length'])]
    all_years_mean = [x for x in m for _ in np.arange(1, 13)]
    all_years = df.loc[df.year == 'all years']
    all_years = all_years.pivot(index='month', columns='year', values='avg_length')

    fig, ax = plt.subplots(figsize=(8, 6))
    # Plot 2012-2017
    ax.plot(each_year)
    # Plot total avg 2012-2017
    ax.plot(all_years, linewidth=4, alpha=0.7)

    ax.plot(np.arange(1, 13), all_years_mean, linestyle="--")

    plt.title(title)
    years.append("all years")
    years.append("avg all years")
    ax.legend(labels=years, loc='upper center', bbox_to_anchor=(0.5, -0.04),
              fancybox=True, ncol=5, fontsize=8)
    xlabels = [x[1] for x in months.values()]
    ax.set_xticks(np.arange(1, 13, 1))
    ax.set_xticklabels(xlabels, fontdict={'fontsize': 8})
    ax.set_ylabel('Article length')
    ax.grid(axis='y', linewidth=0.3)
    fig.text(0.932, 0.450, str('-' + round(all_years_mean[0]).__str__()), ha='center', size="11")
    ax.margins(x=0)

    title = '_'.join(title.split())
    plt.savefig("E:\\figs\\" + title + '.png')
    plt.show()


def avg_article_length_per_month_all_years(data):
    df = pd.DataFrame()
    for m in months:
        mo = data.loc[data['month'] == m]
        df = pd.concat([df, pd.DataFrame({
            'year': 'all years', 'month': [m], 'avg_length': [sum(mo['avg_length']) // len(mo)]
        })])
    return df


def time_of_day(title, df):
    f = pd.DataFrame()
    for year in years_int:
        df2 = df.loc[df.date.dt.year == year]
        for t in range(0, 24, 1):
            df3 = df2.loc[df2.time.dt.hour == t]
            f = pd.concat([f, pd.DataFrame({'time': [t], 'count': [len(df3)], 'year': [year]})])

    f2 = pd.DataFrame()
    for t in range(0, 24, 1):
        df2 = f.loc[f.time == t]
        avg = round(sum(df2['count']) / len(df2['count']))
        f2 = pd.concat([f2, pd.DataFrame({
            'time': [t], 'count': [avg], 'year': ['all years']
        })])

    # f2 = pd.concat([f, f2])
    fig, axes = plt.subplots()
    f = f.pivot(index='time', columns='year', values='count')
    f2 = f2.pivot(index='time', columns='year', values='count')

    axes.set_xticks(np.arange(0, 24, 1))
    axes.set_yticks(np.arange(0, 2601, 200))
    axes.set_ylabel("No. of articles")
    axes.set_xlabel("Hour of day")
    axes.plot(f)
    axes.plot(f2, linewidth=4, alpha=0.7)
    axes.margins(x=0)
    axes.grid(linewidth=0.2)
    plt.legend(years)
    plt.title(title)
    title = '_'.join(title.split())
    plt.savefig('E:\\figs\\' + title + '.png')
    plt.show()


def simple_dist_graph(title, topic=None):
    f = get_df(source=mainfile, drop_nans=True, category=topic)
    nums = []
    for y in years_int:
        df = f.loc[f.date.dt.year == y]
        nums.append(len(df))

    fig, axes = plt.subplots()
    x = np.arange(2012, 2018)
    axes.bar(x, nums, color='darkorange')
    axes.grid(axis='y', linewidth=0.3)
    axes.set_yticks(np.arange(0, 28001, 4000))
    axes.set_ylabel("No. of articles")
    axes.set_xlabel("Year")
    plt.title(title)
    title.replace('No.', 'No')
    title = '_'.join(title.split())
    plt.savefig("E:\\figs\\" + title + '.png')
    plt.show()


if __name__ == '__main__':
    mainfile = 'E:\\data\\corpus_wo_breaklines.csv'
    politics = 'E:\\data\\politics_distribution.csv'
    l_politics = 'E:\\data\\avglength_politics.csv'
    sample = 'E:\\data\\stratified_sample.csv'
    # f = get_df(source=mainfile, dt=True, topic='Politics')
    years = ["2012", "2013", "2014", "2015", "2016", "2017", "all years"]
    years_int = [2012, 2013, 2014, 2015, 2016, 2017]
    d = pd.DataFrame()
    print(d)
    # time_of_day("No. articles published over 24-hours sample", f)
    # topic_distribution_stacked_all(save=True)
    # avg_article_length(f, process=True, title="Average article title length")
    # simple_dist_graph("No. of political articles in each year", topic='Politics')
    # year_month_day_distribution(f, years_int, "Politics distribution sample")
