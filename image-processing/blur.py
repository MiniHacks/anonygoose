import imutils
import cv2
import numpy as np
import os

DETECTION_THRESHOLD = 0.6
COMPARSION_THRESHOLD = 0.8
KERNEL = (40,40)
MARGIN = 0.3
MINIMUM_SIZE = 20

def setup_network(prototxt, model):
    return cv2.dnn.readNetFromCaffe(prototxt, model)

def setup_embedder(model):
    return cv2.dnn.readNetFromTorch(model)

net = setup_network("./image-processing/deploy.prototxt", "./image-processing/res10_300x300_ssd_iter_140000.caffemodel")
embedder = setup_embedder("./image-processing/openface_nn4.small2.v1.t7")

def get_embeddings(image):
    vectorized = []

    # print("Vectorizing image...")

    image = imutils.resize(image, width=600)
    regions = find_faces(image)
    for region in regions:

        (startX, startY, endX, endY) = region

        if endY - startY < MINIMUM_SIZE or endX - startX < MINIMUM_SIZE:
            continue

        face = image[startY:endY, startY:endY]
        
        faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,(96, 96), (0, 0, 0), swapRB=True, crop=False)
        embedder.setInput(faceBlob)
        face_vec = embedder.forward()
        vectorized.append((region, face_vec.flatten()))
        # print("Face vectorized for image.")

    return vectorized

def norm_cross_cor(face1, face2):
    normalized1 = (face1 - np.mean(face1)) / np.linalg.norm(face1)
    normalized2 = (face2 - np.mean(face2)) / np.linalg.norm(face2)
    cor = np.dot(normalized1, normalized2)
    return cor

def compare_faces(face1, face2):
    ncc = norm_cross_cor(face1, face2) 
    return ncc > COMPARSION_THRESHOLD

def find_faces(image):
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    net.setInput(blob)
    detections = net.forward()
    regions = []

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > DETECTION_THRESHOLD:
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

def find_regions_to_blur(image, invalids):
    to_ret = []

    for region, face_vec in get_embeddings(image):
        
        to_cont = False
        for invalid in invalids:
            is_similar = compare_faces(face_vec, invalid)
            if is_similar:
                to_cont = True
                break

        if to_cont:
            continue
        to_ret.append(region)

    return to_ret

def test():
    image = cv2.imread("C:/Users/welsa/Pictures/WIN_20220212_16_20_48_Pro.jpg")

    invalids = []
    folder_path = "C:/Users/welsa/Pictures/test-recognition"
    for filename in os.listdir(folder_path):
        pf = os.path.join(folder_path, filename)
        for f in os.listdir(pf):
            image_path = os.path.join(pf, f)
            to_get = cv2.imread(image_path)
            for _, face_vec in get_embeddings(to_get):
                pass
                invalids.append(face_vec)

    to_blur = find_regions_to_blur(image, invalids)
    blur(image, to_blur)

if __name__ == "__main__":
    test()
