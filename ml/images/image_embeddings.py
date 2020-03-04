#!/usr/bin/env python
"""
    VGG16 feature extraction.
"""
import os

import numpy as np
from PIL import ImageFile
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from keras.preprocessing import image

np.random.seed(2020)
ImageFile.LOAD_TRUNCATED_IMAGES = True

# display model layers
# model.summary()
m = VGG16(weights='imagenet', include_top=True)
# load pre-trained model
base_model = VGG16(weights='imagenet')


# Creates image embeddings by using the VGG16 model.
# Output: An array of feature vector dimensions
def embed_vgg16(files, path):
    try:
        [files[i] for i in range(10)]
    except TypeError:
        print(f"Arg files is an iterable type, it is {type(files)}")
    broken_imgs = []
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
    if len(broken_imgs) > 0:
        print("Images that could not be embedded:")
        for y in broken_imgs:
            print(y)
    print(f"Embedded {len(files) - len(broken_imgs)} images")

# if __name__ == '__main__':
# import pandas as pd
# idpath = "E:/data/27-02-2020-14-16/id_path.csv"
# paths = pd.read_csv(idpath)
# start = time.time()
# embed_vgg16(paths['path'].values, path="E:/data/27-02-2020-14-16/VGG16-embeddings.out")
# end = time.time()
# g = end - start
# print("%.f2" % g)
