import imutils
import cv2
import numpy as np

THRESHOLD = 0.6
KERNEL = (30,30)

def setup_network(prototxt, model):
    return cv2.dnn.readNetFromCaffe(prototxt, model)

net = setup_network("./image-processing/deploy.prototxt", "./image-processing/res10_300x300_ssd_iter_140000.caffemodel")

def blur(image, userid):
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    net.setInput(blob)
    detections = net.forward()
    n = 0

    for i in range(0, detections.shape[2]):

        confidence = detections[0, 0, i, 2]
        if confidence > THRESHOLD:
            n += 1

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            blurred_part = cv2.blur(image[startY:endY, startX:endX], ksize=KERNEL)
            image[startY:endY, startX:endX] = blurred_part

            text = "{:.2f}%".format(confidence * 100) + 'Count ' + str(n)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
            cv2.putText(image, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    cv2.imshow("preview", image)
    cv2.waitKey(0)

def test():
    image = cv2.imread("C:/Users/welsa/Pictures/manicare-blog-face-shapes-inlaid-2.jpg")
    blur(image, None)

if __name__ == "__main__":
    test()
