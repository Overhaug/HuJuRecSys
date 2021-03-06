"""
    A super basic webapp to demonstrate results from similarity functions.
"""
from random import randrange

from flask import Flask, render_template, send_from_directory

from definitions import get_paths
from twpc import utils

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    global refresh
    if refresh == 2399:
        return print("No more unique items to display")
    first_item = [get_item(x) for x in random_indexes(1)]
    next_ids = scores[first_item[0]['id']].nlargest(5)
    print(f"Related articles: \n {next_ids}")
    next_ids = next_ids.index.values.tolist()
    next_ids.remove(first_item[0]['id'])
    next_3 = [get_item(x, by='id') for x in next_ids]
    # items = [get_item(x) for x in random_indexes(5)]
    return render_template('index.html', f_item=first_item[0], n_items=next_3)


@app.route("/random")
def ran():
    items = [get_item(df, x) for x in random_indexes(5)]
    return render_template('random-articles.html', items=items)


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(ospaths["imagedir"], filename, as_attachment=True)


def get_item(i, by="index"):
    if by == "id":
        df2 = df.loc[df.id == i].T.squeeze()
        print(f"Related article: {df2.id}")
    else:  # By index
        df2 = df.loc[df.index[i]]
        print(f"Main article: {df2.id}")
    try:
        image = paths[df2.id]
    except KeyError:
        return
    return {
        "id": df2.id,
        "title": df2.title,
        "image": image,
        "caption": df2.image_caption,
        "author": df2.author,
        "author_bio": df2.author_bio,
        "date_time": str(df2.date) + ", " + str(df2.time),
        "text": df2.text,
        "link": df2.article_url,
    }


def random_indexes(n):
    indexes = []
    for i in range(n):
        def random_int():
            number = randrange(len(df))
            if number not in indexes and number not in displayed:
                indexes.append(number)
            else:
                print(f"{number} already displayed")
                random_int()

        random_int()
    displayed.extend(indexes)
    global refresh
    refresh += 1
    print(f"Refresh number {refresh}")
    return indexes


if __name__ == '__main__':
    refresh = 0
    ospaths = get_paths()
    session = "27-02-2020-14-16"
    session = ospaths["datadir"] + session + "/"
    df = utils.get_df(session + "sample_Politics_400.csv")
    # full = utils.get_df(session + "twp_corpus_html.csv", drop_nans=True)
    paths = utils.get_id_path_pairs(df, from_path="subdir")
    print(f"Loaded location of {len(paths)} images")
    scores = utils.get_pivot(session + "pivot-mean-scores-emb-textTFIDF-bioLV-titleLCS-.csv")
    print(f"Loaded {len(scores)} scores")
    displayed = []
    app.run(host='127.0.0.1', port=8000)
