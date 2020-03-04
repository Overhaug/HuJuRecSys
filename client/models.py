from sqlalchemy import ForeignKey
from sqlalchemy import text
from sqlalchemy.orm import relationship

from client import db
from definitions import get_paths
from utils import get_df

db.metadata.clear()


class Article(db.Model):
    """
        A model that describes an article. Does not separate blogs and news articles, or standalones or compilations.
    """
    __tablename__ = "article"
    id = db.Column(db.String, db.ForeignKey("score.id"), db.ForeignKey("score.referred_id"), primary_key=True)
    article_url = db.Column(db.String)
    title = db.Column(db.String)
    author = db.Column(db.String)
    author_bio = db.Column(db.String)
    text = db.Column(db.String)
    date = db.Column(db.String)
    time = db.Column(db.String)
    category = db.Column(db.String)
    subcategory = db.Column(db.String)
    image_url = db.Column(db.String)
    type = db.Column(db.String)
    subtype = db.Column(db.String)

    def __repr__(self):
        return '<User {}>'.format(self.id)

    @staticmethod
    def update_data(session, dataset):
        print(f"Inserting data into table article")
        ospaths = get_paths()
        session = ospaths["datadir"] + session + "/"
        df = get_df(session + dataset, drop_nans=True)
        df.to_sql(name="article", con=db.engine, index=False, if_exists="replace")


class Score(db.Model):
    """
        Superclass that represent a similarity score between two articles (id, referred_id)
    """
    __tablename__ = "score"
    relation = db.Column(db.Integer, primary_key=True)
    id = db.Column(ForeignKey("score.id"))
    referred_id = db.Column(ForeignKey("score.referred_id"))
    relationship("Article", primaryjoin="Score.id == Article.id")
    relationship("Article", primaryjoin="Score.referred_id == Article.id")
    score = db.Column(db.Float)

    def __init__(self, this_id, referred_id):
        self.id = this_id
        self.referred_id = referred_id

    @staticmethod
    def update_data(session, dataset, mode, tablename):
        print(f"Inserting data into table {tablename}")
        ospaths = get_paths()
        session = ospaths["datadir"] + session + "/"
        df = get_df(session + dataset)
        df.to_sql(name=tablename, con=db.engine, index=False, if_exists=mode)


class LevenshteinScore(Score):
    __tablename__ = "levenshteinscore"

    def __init__(self, this_id, referred_id):
        self.__tablename__ = "levenshteinscore"
        Score.__init__(self, this_id, referred_id)

    @staticmethod
    def update_data(session, dataset, mode, tablename=__tablename__):
        Score.update_data(session, dataset, mode, tablename)


class JaroWinklerScore(Score):
    __tablename__ = "jarowinklerscore"

    def __init__(self, this_id, referred_id):
        self.__tablename__ = "jarowinklerscore"
        Score.__init__(self, this_id, referred_id)

    @staticmethod
    def update_data(session, dataset, mode, tablename=__tablename__):
        Score.update_data(session, dataset, mode, tablename)


class TFIDFScore(Score):
    __tablename__ = "tfidfscore"

    def __init__(self, this_id, referred_id):
        self.__tablename__ = "tfidfscore"
        Score.__init__(self, this_id, referred_id)

    @staticmethod
    def update_data(session, dataset, mode, tablename=__tablename__):
        Score.update_data(session, dataset, mode, tablename)


class ImageEmbeddingScore(Score):
    __tablename__ = "imageembeddingscore"

    def __init__(self, this_id, referred_id):
        self.__tablename__ = "imageembeddingscore"
        Score.__init__(self, this_id, referred_id)

    @staticmethod
    def update_data(session, dataset, mode, tablename=__tablename__):
        Score.update_data(session, dataset, mode, tablename)


def top3_embedding(main_id):
    sql = text("SELECT sc.score, art.* FROM imageembeddingscore sc "
               "inner join article art on art.id = sc.referred_id "
               "where sc.id = :c and sc.id != art.id "
               "order by sc.score desc limit 3;")

    # res = db.engine.execute(sql, x=main_id)
    import pandas as pd
    df = pd.read_sql_query(sql, db.engine, params={"c": main_id})
    return df


def get_random_article(n):
    sql = text("SELECT distinct art.* from imageembeddingscore sc "
               "inner join article art on art.id = sc.id order by random() limit :y;", n)

    return db.engine.execute(sql, y=n).fetchall()
    # return sample.query.order_by(func.random()).limit(n).all()


# Article.update_data("27-02-2020-14-16", "sample_Politics_400.csv")
# JaroWinklerScore.update_data("27-02-2020-14-16/db", "db-jw-scores.csv", mode="replace")

# a = top3_embedding(this_id)
