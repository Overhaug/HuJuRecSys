#!/usr/bin/env python
"""
A messy module to create graphs
"""

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


def year_month_day_distribution(df, title, for_sample=False):
    month_year = get_month_in_year(df)
    width = [3] * len(months)
    height = [2.5] * len(years_int)

    columns = len(months)
    rows = len(years_int)
    fig, ax_array = plt.subplots(rows, columns, squeeze=True, sharey='col',
                                 gridspec_kw={'width_ratios': width, 'height_ratios': height})

    def set_size(w, h):
        """ w, h: width, height in inches """
        ax_array = plt.gca()
        l = ax_array.figure.subplotpars.left
        r = ax_array.figure.subplotpars.right
        t = ax_array.figure.subplotpars.top
        b = ax_array.figure.subplotpars.bottom
        figw = float(w) / (r - l)
        figh = float(h) / (t - b)
        ax_array.figure.set_size_inches(figw, figh)

    set_size(3, 2.5)
    plt.setp(ax_array, ylim=(0, 10))

    n = 0
    for i, ax_row in enumerate(ax_array):
        for j, axes in enumerate(ax_row):
            if i == 5 and j > 7:  # i = years, j = months, here 7 because last year only has 7 months
                axes.set_visible(False)
                continue
            data = month_year[n]
            # Fill in missing days
            y = data.iloc[0].year
            m = data.iloc[0].month
            n_days = calendar.monthrange(y, m)
            month_range = [x for x in range(1, n_days[1] + 1) if x not in data.day.unique().tolist()]
            for day in month_range:
                data = pd.concat([data, pd.DataFrame({"year": [y], "month": [m], "day": [day], "counts": [0]})])
            ###
            data.sort_values(by="day", inplace=True)
            try:
                monday = get_first_monday(data)
                t = np.arange(monday, int(data.day.max()) + 1, 7)
                axes.set(xticks=t, xticklabels=t)
                axes.set_xticks(fontsize=12)
            except TypeError:
                pass  # No Mondays in the current month
            axes.grid(axis='y', linewidth=0.3)
            if for_sample:
                axes.bar(data.day, data.counts)
            else:
                axes.plot(data.day, data.counts)
            n += 1

    for ax, month in zip(ax_array[0], months):
        m = months[month]
        ax.set_title(m[0], size="24")

    for ax, year in zip(ax_array[:, 0], years_int):
        ax.set_ylabel(year, rotation=90, size="24")

    fig.text(0.10, 0.5, 'Year', ha='center', rotation=90, size="27")
    fig.text(0.5, 0.92, 'Month', ha='center', size="27")
    # fig.text(0.68, 0.18, 'x-axis on each subplot represent Mondays', size="16")
    plt.gcf().set_size_inches(50, 20)
    if for_sample:
        plt.setp(ax_array, ylim=(0, 10))
    else:
        plt.setp(ax_array, ylim=(0, 300))
    title = '_'.join(title.split())
    plt.savefig('E:\\figs\\' + title + '.pdf', bbox_inches='tight')
    plt.show()


def get_month_in_year(dates_df):
    month_year_df = []
    for year in years_int:
        year_df = dates_df.loc[dates_df.date.dt.year == int(year)]
        for m in sorted(year_df.date.dt.month.unique()):
            month_df = year_df.loc[year_df.date.dt.month == m]
            current_month = pd.DataFrame()
            for day in month_df.date.dt.day.unique():
                c = len(month_df.loc[month_df.date.dt.day == day])
                current_month = pd.concat(
                    [current_month, pd.DataFrame({'year': [year], 'month': [m], 'day': [day], 'counts': [c]})]
                )
            current_month.sort_values(by=['day'], inplace=True)
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
    without_nans = df
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

    top = df[:10]
    top['color'] = 'red'
    bottom = df[10:]
    bottom['color'] = 'blue'

    # bottom.rename(columns={'size': 'size_bottom'}, inplace=True)
    df2 = pd.concat([top, bottom], sort=False)

    df['size'].plot(kind='bar', color=df2.color, width=0.8, edgecolor="black")
    # bottom['size_bottom'].plot(kind='bar', color=bottom.color, legend=None, ax=ax2)
    plt.xticks(np.arange(0, len(df.category), 1), labels=list(df.category), fontsize=12)
    plt.yticks(np.arange(0, 60001, 2500), fontsize=12)
    plt.ylabel("No. of articles", fontsize=16)
    plt.xlabel("Category", fontsize=16)
    plt.gcf().set_size_inches(12, 8)
    red_patch = mpatches.Patch(color='red', label='Top 10')
    blue_patch = mpatches.Patch(color='blue', label='Bottom 30')
    plt.legend(handles=[red_patch, blue_patch], fontsize=14)

    # plt.title("Category distribution in TREC Washington Post Corpus")
    plt.grid(axis='y', linewidth=0.3)
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    if save is True:
        plt.savefig('E:/figs/' + 'top_overall' + '.pdf')
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
        plt.savefig('E:/figs/' + 'categories_stack_graph_alt' + '.pdf')
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


def avg_article_length(data, process=False, title=None):
    if process:
        temp_df = pd.DataFrame()
        for y in (2012, 2013, 2014, 2015, 2016, 2017):
            data_in_year = data.loc[data['date'].dt.year == y]
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
        save_as_csv(data=data, save_loc="E:\\data\\" + path + ".csv")

    each_year = df[df.year != 'all years']
    each_year = each_year.pivot(index='month', columns='year', values='avg_length')
    all_years_mean = df.loc[df.year == 'all years'].mean()
    m = [(all_years_mean['avg_length'])]
    all_years_mean = [x for x in m for _ in np.arange(1, 13)]
    all_years = data.loc[data.year == 'all years']
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
    # ax.set_xticks(np.arange(1, 13, 1))
    # ax.set_xticklabels(xlabels, fontdict={'fontsize': 8})
    ax.set_ylabel('Article length')
    ax.grid(axis='y', linewidth=0.3)
    fig.text(0.932, 0.450, str('-' + round(all_years_mean[0]).__str__()), ha='center', size="11")
    ax.margins(x=0)

    title = '_'.join(title.split())
    plt.savefig("E:\\figs\\" + title + '.pdf')
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
    plt.savefig('E:\\figs\\' + title + '.pdf')
    plt.show()


def simple_dist_graph(title, df):
    f = df.loc[df.category == "Politics"]
    nums = []
    for y in years_int:
        d = f.loc[f.date.dt.year == y]
        nums.append(len(d))

    fig, axes = plt.subplots()
    plt.gcf().set_size_inches(7, 5)
    x = np.arange(2012, 2018)
    axes.bar(x, nums, color='darkorange')
    axes.grid(axis='y', linewidth=0.3)
    axes.set_yticks(np.arange(0, 12001, 2000))
    axes.set_ylabel("No. of articles", fontsize=14)
    axes.set_xlabel("Year", fontsize=14)
    axes.axhline(sum(nums) / len(nums), color='blue', linewidth=2)
    # plt.title(title)
    title.replace('No.', 'No')
    title = '_'.join(title.split())
    plt.savefig("E:\\figs\\" + title + '.pdf')
    plt.show()


def bar_avg_length(title, data):
    features = ["title", "text", "author_bio", "author"]
    fnames = ["Title", "BodyText", "AuthorBio", "Author"]
    fig, axes = plt.subplots(2, 2, squeeze=True, gridspec_kw={'width_ratios': [1, 1], 'height_ratios': [1, 1]})

    def count(f):
        nums = []
        for y in years_int:
            lm = []
            df_year = data.loc[data.date.dt.year == y]
            for i, row in df_year.iterrows():
                if f == "author":
                    lm.append(len(set(filter(None, row[f].split(";")))))
                else:
                    lm.append(len(row[f].split()))
            try:
                nums.append(sum(lm) / len(lm))
            except ZeroDivisionError:
                pass
        return nums

    def plot(nums, f):
        avg = sum(nums) / len(nums)
        # plt.gcf().set_size_inches(8, 6)
        x = np.arange(2012, 2018)
        if f == "author":
            ax.bar(x, nums, color="seagreen")
            ax.set_yticks(np.arange(0, 1.21, 0.2))
        else:
            ax.bar(x, nums, color="royalblue")
        ax.axhline(avg, color='brown', linewidth=1.5)
        ax.set_axisbelow(True)
        ax.grid(axis='y', linewidth=0.4)
        # ax.set_yticks(np.arange(0, max(nums) + 2, round(max(nums) / 5)))

        ax.set_xticks(np.arange(2012, 2018, 1))
        # ax.set_xlabel(np.arange(2012, 2018, 1), rotation=45)
        # ax.set_ylabel("Avg. length", fontsize=14)
        # ax.set_xlabel("Year", fontsize=14)
        # ax.title()

    n = 0
    for i, ax_row in enumerate(axes):
        for j, ax in enumerate(ax_row):
            plot(count(features[n]), features[n])
            ax.set_title(fnames[n], size="14")
            n += 1
    # plt.title(title)

    for ax, year in zip(axes[:, 0], ["Mean num. words"] * 2):
        ax.set_ylabel(year, rotation=90, size="18")

    u = 0
    for ax, month in zip(axes[1], [1, 2]):
        if u == 1:
            ax.set_ylabel("Mean num. authors", rotation=90, size="18")
        ax.set_xlabel("Year", size="18")
        u += 1

    plt.gcf().set_size_inches(15, 10)
    title = '_'.join(title.split())
    plt.savefig("E:/figs/final/" + title + '.pdf', bbox_inches='tight')
    plt.show()


def simple_dist_graph_subcats(title, data):
    data = data[data.subcategory != "Community Relations"]
    d = pd.DataFrame()
    for s in data.subcategory.unique().tolist():
        d = pd.concat([d, pd.DataFrame({"subcat": [s], "counts": len(data.loc[data.subcategory == s])})])

    d.sort_values(by=['counts'], inplace=True, ascending=True)
    d.reset_index(inplace=True)

    # top = d[-5:]
    # top['color'] = 'red'
    # bottom = d[:-5]
    # bottom['color'] = 'blue'
    # df2 = pd.concat([top, bottom], sort=False)
    # df2.sort_values(by=["counts"], inplace=True, ascending=True)

    # d['counts'].plot(kind='bar', width=0.8, color=df2.color, edgecolor="black")
    # color=df2.color
    plt.barh(d.subcat, d.counts, height=0.8, color="dodgerblue")

    # plt.xticks(np.arange(0, len(data.subcategory.unique().tolist()), 1), labels=list(data.subcategory.unique().tolist()), fontsize=16, rotation=70)
    # plt.yticks(np.arange(0, d.counts.max() + 2000, 2000), fontsize=14, rotation=90)
    plt.yticks(np.arange(0, len(d.subcat.unique().tolist()), 1), labels=list(d.subcat.unique()))
    # plt.xticks(np.arange(0, d.counts.max() + 3000, 3000))
    # plt.ylabel("No. of articles", fontsize=16)
    plt.ylabel("Subcategory", fontsize=16, rotation=90)
    plt.xlabel("Num. articles", fontsize=16)

    plt.gcf().set_size_inches(12, 8)
    plt.grid(axis='x', linewidth=0.3)
    # red_patch = mpatches.Patch(color='red', label='Top ' + str(len(top)))
    # blue_patch = mpatches.Patch(color='blue', label='Bottom ' + str(len(bottom)))
    # plt.legend(handles=[red_patch, blue_patch], fontsize=14, loc="lower right")
    title = "_".join(title.split())
    plt.tight_layout()
    plt.savefig("E:/figs/final/" + title + '.pdf')
    plt.show()


def graph_nauthors_year(title, data):
    nums = []
    for y in years_int:
        d = data.loc[data.date.dt.year == y]
        d["count"] = d.author.apply(lambda a: len(set(filter(None, a.split(";")))))
        nums.append(d["count"].sum() / len(d))

    fig, axes = plt.subplots()
    plt.gcf().set_size_inches(7, 5)
    x = np.arange(2012, 2018)
    avg = sum(nums) / len(nums)
    axes.axhline(avg, color='blue', linewidth=2)
    axes.bar(x, nums, color='darkorange')
    axes.grid(axis='y', linewidth=0.3)
    # axes.set_yticks(np.arange(1, 1.3, 0.2))
    axes.set(ylim=(1, 1.15))
    axes.set_ylabel("No. of authors", fontsize=14)
    axes.set_xlabel("Year", fontsize=14)
    # plt.title(title)
    title = '_'.join(title.split())
    plt.savefig("E:\\figs\\" + title + '.pdf')
    plt.show()


def avg_sentiment(title, data):
    sentiments = pd.read_csv("E:/data/Final/text-sentiment.csv")
    nums = []
    for y in years_int:
        ids_in_year = data.loc[data.date.dt.year == y]
        sents = sentiments[sentiments.id.isin(ids_in_year.id.values.tolist())]
        nums.append(np.var(sents.sentiment.tolist()))

    fig, axes = plt.subplots()
    plt.gcf().set_size_inches(7, 5)
    x = np.arange(2012, 2018)
    avg = sum(nums) / len(nums)
    axes.axhline(avg, color='blue', linewidth=2)
    axes.bar(x, nums, color='darkorange')
    axes.grid(axis='y', linewidth=0.3)
    # axes.set_yticks(np.arange(1, 1.3, 0.2))
    axes.set_ylabel("No. of authors", fontsize=14)
    axes.set_xlabel("Year", fontsize=14)
    # plt.title(title)
    title = '_'.join(title.split())
    plt.savefig("E:\\figs\\" + title + '.pdf')
    plt.show()


if __name__ == '__main__':
    mainfile = 'E:\\data\\twp_corpus_plain2.csv'
    # df = get_df(source=mainfile, dt=True, drop_nans=True, drop_duplicates=True, drop_missing_bio=True, has_image=True)
    years = ["2012", "2013", "2014", "2015", "2016", "2017", "all years"]
    years_int = [2012, 2013, 2014, 2015, 2016, 2017]

    # df = get_df(source=mainfile, dt=True, drop_nans=True, drop_duplicates=True, drop_missing_bio=True, has_image=True)
    df = get_df(source="E:/data/twp_corpus_plain_proc.csv", dt=True)
    df3 = df.loc[df.category == "D.C., Md. & Va."]
    dfs = df.loc[df.category == "Sports"]
    df2 = df.loc[df.category == "Politics"]
    # df = get_df(source=mainfile, dt=True, drop_nans=True, drop_duplicates=True, drop_missing_bio=True, has_image=True)
