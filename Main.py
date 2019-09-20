import json_lines as jl
import json

num_of_articles = 10000

articles = []
with open('../Data/WashingtonPost.v2/data/TREC_Washington_Post_collection.v2.jl', 'rb') as f:
    num = 0
    for item in jl.reader(f):
        print(item)
        break
        if item['type'] == "article":
            articles.append(item)
            print(num, 'of ', num_of_articles)
        if len(articles) == num_of_articles:
            print('Limit reached')
            break
        num += 1
    f.close()


def write_to_file():
    with open('../Data/WashingtonPost.v2/data/snippet.json', 'w', encoding='utf-8') as x:
        for z in articles:
            x.write(json.dumps(z, indent=4, ensure_ascii=False))

        print('Wrote to file')

        x.close()

