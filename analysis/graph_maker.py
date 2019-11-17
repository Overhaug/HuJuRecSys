import pandas as pd
import matplotlib.pyplot as plt

months = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}


def no_of_articles_per_month_for_a_year(dates_df, year, save=False):
    year_df = dates_df.loc[dates_df.dt.year == int(year)]

    year_df.groupby([year_df.dt.month]).count().plot(kind="bar")
    plt.title("No. of news items per month for " + str(year))
    if save is True:
        plt.savefig('D:/newsRecSys/data/figs/' + 'articles_per_month_for_' + str(year) + '.pdf')
    plt.show()
    plt.close()


def no_of_articles_per_year_for_a_month(dates_df, month, save=False):
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


def get_dates_as_dt_df():
    df = pd.read_csv('D:/newsRecSys/data/corpus_csv.csv').dropna()
    return pd.to_datetime(df['published_date'], format='%Y-%m-%d', errors='coerce')


if __name__ == '__main__':
    dates = get_dates_as_dt_df()
    years = (2011, 2012, 2013, 2014, 2015, 2016, 2017)
    for y in years:
        no_of_articles_per_month_for_a_year(dates, y, save=True)
    for m in months:
        no_of_articles_per_year_for_a_month(dates, m, save=True)

    no_of_articles_per_year(dates, save=True)
    no_of_articles_per_month_all_years(dates, save=True)
