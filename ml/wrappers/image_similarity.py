import os

import pandas as pd
from sklearn.preprocessing import normalize

import common
import image_feature_extraction
import utils


def embeddings_cosine_sim(file, sp, df):
    print("Computing cosine similarity across image embeddings")
    create_embeddings(file[:file.rfind("/") + 1])
    id_embeddings = utils.get_out_file(file)
    embeddings = id_embeddings["embedding"].tolist()
    print("Normalizing image embeddings")
    normalized_embeddings = normalize(embeddings)
    common.cosine_similarity(vectors=normalized_embeddings, df=df, sp=sp)


def create_embeddings(session):
    """
        Creates embeddings for the appropriate images if they do not exist in the session.
    """
    if os.path.exists(session + "id_path.csv") and not os.path.exists(session + "VGG16-embeddings.out"):
        print("Embedding images in current session")
        from images.image_embeddings import embed_vgg16
        idpath = session + "id_path.csv"
        paths = pd.read_csv(idpath)
        embed_vgg16(paths['path'].values, path=session + "VGG16-embeddings.out")


def image_sharpness(sp, sp2, df, update):
    if update:
        image_feature_extraction.image_sharpness(sp, df)
    common.compute_distance(sp, sp2, "sharpness", True)


def image_shannon(sp, sp2, df, update):
    if update:
        image_feature_extraction.image_shannon_entropy(sp, df)
    common.compute_distance(sp, sp2, "shannon", True)


def image_calculate_computed_metrics(sp, sp2, feature):
    data = utils.get_for_feature(sp, feature)
    common.compute_distance(data, sp2, feature, False)


def preload(dirpath):
    image_feature_extraction.load_images_as_greyscale(dirpath)


def clear():
    image_feature_extraction.clear()
