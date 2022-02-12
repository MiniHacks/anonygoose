import imutils
import cv2
import numpy as np
import os

THRESHOLD = 0.6
KERNEL = (30,30)
MARGIN = 0.25
MINIMUM_SIZE = 20

def setup_network(prototxt, model):
    return cv2.dnn.readNetFromCaffe(prototxt, model)

def setup_embedder(model):
    return cv2.dnn.readNetFromTorch(model)

net = setup_network("./image-processing/deploy.prototxt", "./image-processing/res10_300x300_ssd_iter_140000.caffemodel")
embedder = setup_embedder("./image-processing/openface_nn4.small2.v1.t7")

def get_face_embeddings(userid):
    pass # set this up to get faces from the db.

def train_to_ignore(training_sets):
    to_ret = []
    for set in training_sets:
        embeddings = []

        i = 0
        for image in set:
            print("Vectorizing image", i, "...")
            i += 1

            image = imutils.resize(image, width=600)

            regions = find_faces(image, None)
            for (startX, startY, endX, endY) in regions:

                if endY - startY < MINIMUM_SIZE or endX - startX < MINIMUM_SIZE:
                    continue

                face = image[startY:endY, startY:endY]
                
                faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,(96, 96), (0, 0, 0), swapRB=True, crop=False)
                embedder.setInput(faceBlob)
                face_vec = embedder.forward()
                embeddings.append(face_vec.flatten())
                print("Face vectorized for image", i, ":)")

                # Assume only one face per image.
                break
        
        to_ret.append(embeddings)
    return to_ret


def find_faces(image, to_ignore):
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    net.setInput(blob)
    detections = net.forward()
    regions = []

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > THRESHOLD:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            regions.append(box.astype("int"))

    return regions

def blur(image, regions):
    (h, w) = image.shape[:2]
    to_ret = image.copy()

    for (startX, startY, endX, endY) in regions:

        yMargin = (MARGIN * (endY - startY)) / 2.0
        xMargin = (MARGIN * (endX - startX)) / 2.0
        startY = int(startY - yMargin)
        endY = int(endY + yMargin)
        startX = int(startX - xMargin)
        endX = int(endX + xMargin)

        startY = 0 if startY < 0 else startY
        endY = h if endY > h else endY
        startX = 0 if startX < 0 else startX
        endX = w if endX > w else endX

        blurred_part = cv2.blur(to_ret[startY:endY, startX:endX], ksize=KERNEL)
        to_ret[startY:endY, startX:endX] = blurred_part

        cv2.rectangle(to_ret, (startX, startY), (endX, endY), (0, 0, 255), 2)

    cv2.imshow("preview", to_ret)
    cv2.waitKey(0)

    return to_ret

def test():
    image = cv2.imread("C:/Users/welsa/Pictures/WIN_20220212_16_20_48_Pro.jpg")

    to_train = []
    folder_path = "C:/Users/welsa/Pictures/test-recognition"
    for filename in os.listdir(folder_path):
        f = os.path.join(folder_path, filename)
        to_train.append(cv2.imread(f))

    models = train_to_ignore([to_train])

    blur(image, find_faces(image, None))

if __name__ == "__main__":
    test()
