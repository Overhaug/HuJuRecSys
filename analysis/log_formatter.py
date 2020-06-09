#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
from datetime import datetime

import pandas as pd

PAIRS_FILENAME = "SIM-online-survey-out-pairs-test.csv"
PAIRS_DEMOFILE = "SIM-online-survey-out-demo-test.csv"

USE_START_COLS = [0, 1, 3]
START_COLS = ["date", "status", "id"]

USE_SURVEY_COLS = [0, 3, 5, 7, 9, 11, 13, 15, 17]
SURVEY_COLS = ["date", "id", "rating", "pair", "fam1",
               "fam2", "conf", "rand", "step"]

USE_Q_COLS = [0, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27]
Q_COLS = ["date", "id", "age", "gender", "newsws", "days_news", "subcat",
          "title", "image", "author", "datetime", "text", "sentiment", "author_bio"]

STEPS_REQUIRED = [_ for _ in range(1, 11)]  # 1 ... 10

months = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}


def get_logs(ldir: str):
    return glob.glob(ldir + "/*logfile.txt")


def parse_logs(ldir: str):
    logs = get_logs(ldir)
    scores = pd.read_csv("E:/data/Final/formatted/all_scores.csv")

    parsed_pairs = pd.DataFrame()
    parsed_questionnaires = pd.DataFrame()

    incomplete_questionnaire = 0
    incomplete_survey_questions = 0

    for i, log in enumerate(logs):
        start, survey, questionnaire = process_log(log)

        if questionnaire is None or questionnaire.empty:
            print(f"[{i}] Log {log} did not fill out the final questionnaire.")
            incomplete_questionnaire += 1
            continue
        if survey is None or survey.empty or len(survey.step.unique()) < 10:
            print(f"[{i}] Log {log} did not complete the survey questions.")
            incomplete_survey_questions += 1
            continue

        survey = last_recorded_step(survey)

        survey["dt_col"] = survey["date"].apply(lambda x: dt_col(x))
        survey = timediff(survey, start)

        survey[["r1", "r2"]] = survey.pair.str.split(";", expand=True)
        pairs = survey[["r1", "r2"]]
        survey.drop(["pair", "r1", "r2"], axis=1, inplace=True)
        survey.insert(2, "r1", pairs["r1"])
        survey.insert(3, "r2", pairs["r2"])

        survey = find_scores_for_pair(survey, scores)

        attention_check = survey.loc[survey.step == survey.rand].T.squeeze()
        questionnaire["passed"], survey["passed"] = passed_check(attention_check)
        questionnaire["finished"], survey["finished"] = finished_survey(survey)

        shared_cols = list(set(survey.columns.tolist()) & set(questionnaire.columns.tolist()))
        survey["id2"] = [questionnaire.iloc[0].id for _ in range(len(survey))]
        survey["date2"] = [questionnaire.iloc[0].date for _ in range(len(survey))]
        survey = pd.concat([survey, pd.concat([questionnaire.drop(shared_cols, axis=1)] * 10,
                                              ignore_index=True)], axis=1)

        parsed_pairs = pd.concat([parsed_pairs, survey])
        parsed_questionnaires = pd.concat([parsed_questionnaires, questionnaire])

    print(f"Logs with incomplete survey questions: {incomplete_survey_questions}")
    print(f"Logs with incomplete survey questionnaire: {incomplete_questionnaire}")
    print(f"Parsed survey questions: {len(parsed_pairs)}")
    print(f"Parsed questionnaires: {len(parsed_questionnaires)}")
    parsed_pairs.to_csv("E:/data/logs/parsed/" + PAIRS_FILENAME, index=False, sep="\t")
    parsed_questionnaires.to_csv("E:/data/logs/parsed/" + PAIRS_DEMOFILE, index=False, sep="\t")


def process_log(log: str):
    """
    Reads in a log one line at a time.
    Determines if the line belongs to the start, survey, or finish part of the survey.
    The indexes for each type of line are stored, and the log is queried once for each type where it fetches the
    corresponding lines.
    :param log: path to a survey log
    :return: three DataFrames, one for each part of the survey (start, survey, finish).
    """
    starts = {"rows": []}
    surveys = {"rows": []}
    finishes = {"rows": []}
    i = 0
    while True:
        this = pd.read_csv(log, sep="\t", usecols=[1], names=["status"], nrows=1, skiprows=i)
        if this.empty:
            break
        elif this.status.all() == "(start)":
            starts["rows"].append(i)
        elif this.status.all() == "(survey)":
            surveys["rows"].append(i)
        elif this.status.all() == "(finish)":
            finishes["rows"].append(i)
        i += 1

    def get_starts():
        if len(starts["rows"]) > 0:
            rows_to_ignore = surveys["rows"] + finishes["rows"]
            if len(starts["rows"]) > 1:
                rows_to_ignore = rows_to_ignore + finishes["rows"][:-1]  # Grab last start if more than 1
            return pd.read_csv(log, sep="\t", usecols=USE_START_COLS,
                               names=START_COLS, skiprows=rows_to_ignore)

    def get_surveys():
        if len(surveys["rows"]) > 0:
            rows_to_ignore = starts["rows"] + finishes["rows"]
            return pd.read_csv(log, sep="\t", usecols=USE_SURVEY_COLS,
                               names=SURVEY_COLS, skiprows=rows_to_ignore).dropna()

    def get_questionnaires():
        if len(finishes["rows"]) > 0:
            rows_to_ignore = starts["rows"] + surveys["rows"]
            if len(finishes["rows"]) > 1:
                rows_to_ignore = rows_to_ignore + finishes["rows"][:-1]  # Grab last questionnaire if more than 1
            return pd.read_csv(log, sep="\t", usecols=USE_Q_COLS, names=Q_COLS,
                               skiprows=rows_to_ignore)

    return get_starts(), get_surveys(), get_questionnaires()


def last_recorded_step(survey):
    last_of_each_step = pd.DataFrame()
    for i in STEPS_REQUIRED:
        step = survey.loc[survey.step.values.astype(int) == i]
        last_of_each_step = pd.concat([last_of_each_step, step.tail(1)])
    return last_of_each_step.reset_index(drop=True)


def timediff(survey, start):
    start["dt_col"] = dt_col(start.iloc[0].date)
    for i, row in survey.iterrows():
        if i == 0:
            survey.loc[i, "timediff"] = \
                (max(row["dt_col"], start.iloc[0]["dt_col"]) - min(row["dt_col"], start.iloc[0]["dt_col"])).seconds
            continue
        try:
            survey.loc[i, "timediff"] = \
                (max(survey.iloc[i - 1]["dt_col"], row["dt_col"]) - min(survey.iloc[i - 1]["dt_col"], row["dt_col"])) \
                    .seconds
        except IndexError:
            break
    survey.drop("dt_col", axis=1, inplace=True)
    return survey


def dt_col(d):
    d = d.replace("[", "").replace("]", "").replace("/", "").replace(":", "")
    day, month, year, hour, minute, second = d[0:2], months[d[2:5]], d[5:9], d[9:11], d[11:13], d[13:15]
    date = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    return date


def passed_check(acheck):
    if not acheck.empty and float(acheck["rating"]) == 5 and float(acheck["fam1"]) == 5 \
            and float(acheck["fam2"]) == 5 and float(acheck["conf"] == 5):
        return "TRUE", "TRUE"
    return "FALSE", "FALSE"


def finished_survey(pairs):
    if pairs.step.values.tolist() == STEPS_REQUIRED:
        return "TRUE", "TRUE"
    return "FALSE", "FALSE"


def find_scores_for_pair(pairs, scores):
    s = pd.merge(pairs, scores, left_on=["r1", "r2"], right_on=["first", "second"]) \
        .drop(["first", "second"] + pairs.columns.tolist(), axis=1)
    means = s.mean(axis=1)
    s.insert(0, "all", means)
    return pd.concat([pairs, s], axis=1)


def check_log():
    questionnaires = pd.read_csv("E:/data/logs/parsed/SIM-online-survey-out-demo.csv", sep="\t")
    surveys = pd.read_csv("E:/data/logs/parsed/SIM-online-survey-out-pairs.csv", sep="\t")
    times = []
    for i in surveys.id.unique().tolist():
        user = surveys.loc[surveys.id == i]
        minutes = user.timediff.sum() / 60
        times.append(minutes)
    times.sort()
    print()


def trattner_log():
    df = pd.read_csv("C:/dev/analysis/SIM-online-survey-out-pairs.csv", sep="\t")
    print(len(df))
    ids = df.id.values.tolist()

    for i in ids:
        d = df.loc[df.id == i]
        if len(d) > 9:
            print()


check_log()

# parse_logs("E:/data/logs")
