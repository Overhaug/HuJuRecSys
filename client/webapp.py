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
    first_item = [get_item(x) for x in random_indexes(1)]
    next_ids = tfidf[first_item[0]['id']].nlargest(4)
    print(f"Related articles: \n {next_ids}")
    next_ids = next_ids.index.values.tolist()
    next_ids.remove(first_item[0]['id'])
    next_3 = [get_item(x, by='id') for x in next_ids]
    # items = [get_item(x) for x in random_indexes(5)]
    return render_template('index.html', f_item=first_item[0], n_items=next_3)


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory("E:/images/Sorted/", filename, as_attachment=True)


def get_item(i, by='index'):
    if by == 'id':
        df2 = df.loc[df.id == i].T.squeeze()
        print(f"Related article: {df2.id}")
    else:  # By index
        df2 = df.loc[df.index[i]]
        print(f"Main article: {df2.id}")
    try:
        image = paths[df2.id].replace("\\", "/")
    except KeyError:
        print(f"{df2.id} has no main image!")
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


refresh = 0
df = utils.get_df("E:/data/stratified_politics_sample_html.csv", drop_nans=False)
paths = utils.get_id_path_pairs(df, from_path="subdir")
print("Loaded image directory")
tfidf = utils.get_pivot("E:\\data\\tfidf_pivot.csv")
print("Loaded TFIDF scores")
displayed = []
app.run()
