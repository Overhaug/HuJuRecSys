import os

import pandas as pd
from sklearn.preprocessing import normalize

import common
import utils


def embeddings_cosine_sim(file, sp, df, db):
    print("Computing cosine similarity across image embeddings")
    id_embeddings = utils.get_out_file(file)
    embeddings = id_embeddings["embedding"].tolist()
    print("Normalizing image embeddings")
    normalized_embeddings = normalize(embeddings)
    common.cosine_similarity(vectors=normalized_embeddings, df=df, sp=sp, db=db)


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
