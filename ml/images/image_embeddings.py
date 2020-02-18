# VGG16 feature extraction
# import matplotlib.pyplot as plt
import os

import numpy as np
import pandas as pd
from PIL import ImageFile
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input  # , decode_predictions
from keras.models import Model
from keras.preprocessing import image

from twpc.utils import onedim_list_of_paths

np.random.seed(2018)
ImageFile.LOAD_TRUNCATED_IMAGES = True

# load pre-trained model
# display model layers
# model.summary()

# load pre-trained model
base_model = VGG16(weights='imagenet')


# Creates image embeddings by using the VGG16 model.
# Output: An array of feature vector dimensions
def embed_vgg16(files, path=None):
    model = VGG16(weights='imagenet', include_top=True)
    broken_imgs = []
    if path is None:
        path = os.path.curdir + "/VGG16-embeddings.out"
    with open(path, "a") as f:
        for i, img_ in enumerate(files):
            try:
                head, tail = os.path.split(img_)
                img = image.load_img(img_, target_size=(224, 224))
                img = image.img_to_array(img)
                img = np.expand_dims(img, axis=0)
                img = preprocess_input(img)
                # define model from base model for feature extraction from fc1 layer
                model = Model(input=base_model.input, output=base_model.get_layer('fc1').output)
                # obtain the output of fc1 layer
                fc1_features = model.predict(img)
                print(f"{i}\t{img_}: Feature vector dimensions: ", fc1_features)
                f.write(tail + ",")
                np.savetxt(f, fc1_features, delimiter=',', fmt='%.6f')  # .16f
            except OSError:
                print(f"{img_} cannot be identified. The file is probably corrupted.")
                broken_imgs.append(img_)
    print("Images that could not be embedded:")
    for y in broken_imgs:
        print(y)


# Creates a .CSV file containing ID for every appropriate article, and PATH for each main image related to each ID
def get_applicable_paths(topic=None):
    file_ids = {}

    # Checks if arg. "s", a path to an image, is an instance of the first image found in the TWPC dataset
    # Returns True if the above is True, and the image's ID exists in the appropriate DataFrame
    def is_applicable(path):
        last = str(path).rfind("-")
        next_last = last + 2
        i = path.rfind("\\")
        this_id = path[i + 1:last]
        if this_id not in ids:
            return False
        if path[last + 1:next_last] == "0":
            ids.remove(this_id)
            file_ids[this_id] = path
            return True
        return False

    files = onedim_list_of_paths()
    df = pd.read_csv("E:\\data\\corpus_wo_breaklines.csv").dropna()
    if topic is not None:
        df = df.loc[df.category == topic]
    ids = df.id.tolist()
    [is_applicable(f) for f in files]  # Applicable ID and Paths are stored in file_ids

    m = pd.DataFrame({'id': list(file_ids.keys()), 'paths': list(file_ids.values())})
    m.to_csv("E:/data/id_path_politics.csv")


j = pd.read_csv("E:/data/id_path_politics.csv")

embed_vgg16(j['paths'].values, path="E:/data/VGG16_embeddings.out")

