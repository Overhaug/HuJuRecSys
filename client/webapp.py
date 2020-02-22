# A super basic webapp to demonstrate results from similarity functions
from random import randrange

from flask import Flask, render_template, send_from_directory

from twpc import utils

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    global refresh
    if refresh == 2399:
        return print("No more unique items to display")
    items = [get_item(x) for x in random_indexes(5)]
    return render_template('index.html', items=items)


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory("E:/images/Sorted/", filename, as_attachment=True)


def get_item(i):
    df2 = df.loc[df.index[i]]
    print(f"Article: {df2.id}")
    title = df2.title
    try:
        image = paths[df2.id].replace("\\", "/")
    except KeyError:
        print(f"{df2.id} has no main image!")
        return
    caption = df2.image_caption
    author = df2.author
    author_bio = df2.author_bio
    date_time = str(df2.date.date()) + ", " + str(df2.time.time())
    text = df2.text
    link = df2.article_url
    return {
        "title": title,
        "image": image,
        "caption": caption,
        "author": author,
        "author_bio": author_bio,
        "date_time": date_time,
        "text": text,
        "link": link
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


refresh = 0
df = utils.get_df("E:\\data\\stratified_politics_sample_html.csv", drop_nans=True)
print(f"{len(df)} articles loaded")
paths = utils.get_id_path_pairs(df, from_path="subdir")
displayed = []
app.run()
