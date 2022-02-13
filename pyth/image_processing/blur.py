import imutils
import cv2
import numpy as np
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pathlib import Path
from bson.objectid import ObjectId

DETECTION_THRESHOLD = 0.4
COMPARSION_THRESHOLD = 0.69 # Nice
KERNEL = (80,80)
MARGIN = 0.15
MINIMUM_SIZE = 20
MONGO_URL = os.getenv("MONGO")
MEMORY_LENGTH = 4

def setup_mongo(url):
    return MongoClient(url)

def setup_network(prototxt, model):
    return cv2.dnn.readNetFromCaffe(prototxt, model)

def setup_embedder(model):
    return cv2.dnn.readNetFromTorch(model)

module_dir = Path(__file__).absolute().parent
net = setup_network(str(module_dir / "deploy.prototxt"), str(module_dir / "res10_300x300_ssd_iter_140000.caffemodel"))
embedder = setup_embedder(str(module_dir / "openface_nn4.small2.v1.t7"))
mongo = setup_mongo(MONGO_URL)

def get_embeddings(image):
    vectorized = []

    # print("Vectorizing image...")

    (h, w) = image.shape[:2]
    image = imutils.resize(image, width=600)
    (nh, nw) = image.shape[:2]

    hs = h / nh
    ws = w / nw

    regions = find_faces(image)
    for region in regions:

        (startX, startY, endX, endY) = region

        if endY - startY < MINIMUM_SIZE or endX - startX < MINIMUM_SIZE:
            continue

        face = image[startY:endY, startX:endX]
        
        faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,(96, 96), (0, 0, 0), swapRB=True, crop=False)
        embedder.setInput(faceBlob)
        face_vec = embedder.forward()

        region = (int(startX * ws), int(startY * hs), int(endX * ws), int(endY * hs))

        vectorized.append((region, face_vec))
        # print("Face vectorized for image.")

    return vectorized

def norm_cross_cor(face1, face2):
    normalized1 = np.squeeze((face1 - np.mean(face1)) / np.linalg.norm(face1))
    normalized2 = np.squeeze((face2 - np.mean(face2)) / np.linalg.norm(face2))
    cor = np.dot(normalized1, normalized2)
    return cor

def compare_faces(face1, face2):
    ncc = norm_cross_cor(face1, face2) 
    # print(ncc)
    return ncc > COMPARSION_THRESHOLD

def find_faces(image):
    (h, w) = image.shape[:2]
    resized = cv2.resize(image, (300, 300))
    blob = cv2.dnn.blobFromImage(resized, 1.0, (300, 300), (104.0, 177.0, 123.0))

    regions = []

    net.setInput(blob)
    detections = net.forward()

    for i in range(0, detections.shape[2]):

        confidence = detections[0, 0, i, 2]
        if confidence > DETECTION_THRESHOLD:

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            region = box.astype("int")
            regions.append(region)

    return regions

def blur_regions(image, regions, preview=False):
    (h, w) = image.shape[:2]
    to_ret = image.copy()

    for thing in regions:
        (startX, startY, endX, endY) = thing[0]

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

        # if preview:
        #     cv2.rectangle(to_ret, (startX, startY), (endX, endY), (0, 0, 255), 2)
    if preview:
        cv2.imshow("preview", to_ret)
        cv2.waitKey(0)

    return to_ret

memory = {}
def find_regions_to_blur(image, invalids, userid):
    global memory
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
        to_ret.append([region, MEMORY_LENGTH])

    if userid in memory:
        for region, length in memory[userid]:
            nl = length - 1
            if nl > 0:
                to_ret.append([region, length - 1])

    memory[userid] = to_ret
    return to_ret

def load_mongo_image(path):
    return cv2.imread(path) # TODO: Check if we need to transform this path.

def get_images_from_userID(userID):
    anonynews_db = mongo["anonynews"]
    images_col = anonynews_db["images"]
    image_docs = images_col.find({"user": userID})

    images =  []
    for doc in image_docs:
        image = load_mongo_image(doc["path"])
        images.append(image)
    return images

def get_user_target_uri(user_id):
    anonynews_db = mongo["anonynews"]
    users = anonynews_db["accounts"].find({"userId": ObjectId(user_id)})
    try:
        return next(iter(users)).get("targetRTMPUri", None)
    except StopIteration:
        raise LookupError("no user with that userid :/")

face_vecs_cache = {}
def get_invalid_face_vecs(userID):
    global face_vecs_cache
    if userID in face_vecs_cache:
        return face_vecs_cache[userID]

    images = get_images_from_userID(userID)
    to_ret = []
    for image in images:
        for _, face_vec in get_embeddings(image):
            to_ret.append(face_vec)
    face_vecs_cache[userID] = to_ret
    return to_ret

def blur(frame, userID):
    invalids = get_invalid_face_vecs(userID)
    to_blur = find_regions_to_blur(frame, invalids, userID)
    to_ret = blur_regions(frame, to_blur)
    return to_ret

def test():
    image = cv2.imread("C:/Users/welsa/Pictures/20220213_095018_25.jpg")

    invalids = []
    folder_path = "C:/Users/welsa/Pictures/test-recognition"
    for filename in os.listdir(folder_path):
        pf = os.path.join(folder_path, filename)
        for f in os.listdir(pf):
            image_path = os.path.join(pf, f)
            to_get = cv2.imread(image_path)
            for _, face_vec in get_embeddings(to_get):
                invalids.append(face_vec)

    to_blur = find_regions_to_blur(image, invalids, "0")
    blur_regions(image, to_blur, preview=True)

if __name__ == "__main__":
    load_dotenv()
    cap = cv2.VideoCapture("C:/Users/welsa/Pictures/Camera Roll/WIN_20220213_12_46_59_Pro.mp4")
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    capOut = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if capOut is None:
            capOut = cv2.VideoWriter("C:/Users/welsa/Pictures/Camera Roll/blurrred.mp4", fourcc, 30, (frame.shape[1], frame.shape[0]))

        capOut.write(blur(frame, "0"))


    # print(repr(get_user_target_uri("62083c5e653f72b04624352c")))
