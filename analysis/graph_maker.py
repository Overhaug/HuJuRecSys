import pandas as pd
import matplotlib.pyplot as plt

months = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}


def no_of_articles_per_month_for_a_year(dates_df, years, save=False):
    for year in years:
        year_df = dates_df.loc[dates_df.dt.year == int(year)]

        year_df.groupby([year_df.dt.month]).count().plot(kind="bar")
        plt.title("No. of news items per month for " + str(year))
        if save is True:
            plt.savefig('D:/newsRecSys/data/figs/' + 'articles_per_month_for_' + str(year) + '.pdf')
        plt.show()
        plt.close()


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


def overall_distribution(dates_df, years, save=False):
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


def topic_distribution(data, save=False):
    plt.figure(figsize=(12, 8))
    plt.title("Topics")
    topics = data.topic.unique()

    for y in topics:
        print(y)

    # plt.legend([topic for topic in topics])
    plt.show()
    plt.close()


def get_df(drop_nans=True, only_dates=False):
    df = pd.read_csv('D:/newsRecSys/data/sample.csv')
    if only_dates is True:
        df = pd.to_datetime(df['published_date'], format='%Y-%m-%d', errors='coerce')
    if drop_nans is True:
        df.dropna()
    return df


if __name__ == '__main__':
    dates = get_df(only_dates=True)
    # no_of_articles_per_month_for_a_year(dates, (2011, 2012, 2013, 2014, 2015, 2016, 2017))
    # no_of_articles_per_year_for_a_month(dates, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
    # no_of_articles_per_year(dates)
    # no_of_articles_per_month_all_years(dates)
    overall_distribution(dates, (2011, 2012, 2013, 2014, 2015, 2016, 2017))
    # no_of_articles_per_day_overall(dates)

