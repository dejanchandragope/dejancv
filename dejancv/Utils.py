
import copy
import urllib.request
import cv2
import numpy as np


def stackImages(_imgList, cols, scale):

    imgList = copy.deepcopy(_imgList)

    # Get dimensions of the first image
    width1, height1 = imgList[0].shape[1], imgList[0].shape[0]

    # make the array full by adding blank img, otherwise the openCV can't work
    totalImages = len(imgList)
    rows = totalImages // cols if totalImages // cols * cols == totalImages else totalImages // cols + 1
    blankImages = cols * rows - totalImages

    # Create a blank image with dimensions of the first image
    imgBlank = np.zeros((height1, width1, 3), np.uint8)
    imgList.extend([imgBlank] * blankImages)

    # resize the images to be the same as the first image and apply scaling
    for i in range(cols * rows):
        imgList[i] = cv2.resize(imgList[i], (width1, height1), interpolation=cv2.INTER_AREA)
        imgList[i] = cv2.resize(imgList[i], (0, 0), None, scale, scale)

        if len(imgList[i].shape) == 2:  # Convert grayscale to color if necessary
            imgList[i] = cv2.cvtColor(imgList[i], cv2.COLOR_GRAY2BGR)

    # put the images in a board
    hor = [imgBlank] * rows
    for y in range(rows):
        line = []
        for x in range(cols):
            line.append(imgList[y * cols + x])
        hor[y] = np.hstack(line)
    ver = np.vstack(hor)
    return ver


def cornerRect(img, bbox, l=30, t=5, rt=1,
               colorR=(255, 0, 255), colorC=(0, 255, 0)):

    x, y, w, h = bbox
    x1, y1 = x + w, y + h
    if rt != 0:
        cv2.rectangle(img, bbox, colorR, rt)
    # Top Left  x,y
    cv2.line(img, (x, y), (x + l, y), colorC, t)
    cv2.line(img, (x, y), (x, y + l), colorC, t)
    # Top Right  x1,y
    cv2.line(img, (x1, y), (x1 - l, y), colorC, t)
    cv2.line(img, (x1, y), (x1, y + l), colorC, t)
    # Bottom Left  x,y1
    cv2.line(img, (x, y1), (x + l, y1), colorC, t)
    cv2.line(img, (x, y1), (x, y1 - l), colorC, t)
    # Bottom Right  x1,y1
    cv2.line(img, (x1, y1), (x1 - l, y1), colorC, t)
    cv2.line(img, (x1, y1), (x1, y1 - l), colorC, t)

    return img


def findContours(img, imgPre, minArea=1000, maxArea=float('inf'), sort=True,
                 filter=None, drawCon=True, c=(255, 0, 0), ct=(255, 0, 255),
                 retrType=cv2.RETR_EXTERNAL, approxType=cv2.CHAIN_APPROX_NONE):

    conFound = []
    imgContours = img.copy()
    contours, hierarchy = cv2.findContours(imgPre, retrType, approxType)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if minArea < area < maxArea:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            if filter is None or len(approx) in filter:
                if drawCon:
                    cv2.drawContours(imgContours, cnt, -1, c, 3)
                    x, y, w, h = cv2.boundingRect(approx)
                    cv2.putText(imgContours, str(len(approx)), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ct, 2)
                cx, cy = x + (w // 2), y + (h // 2)
                cv2.rectangle(imgContours, (x, y), (x + w, y + h), c, 2)
                cv2.circle(imgContours, (x + (w // 2), y + (h // 2)), 5, c, cv2.FILLED)
                conFound.append({"cnt": cnt, "area": area, "bbox": [x, y, w, h], "center": [cx, cy]})

    if sort:
        conFound = sorted(conFound, key=lambda x: x["area"], reverse=True)

    return imgContours, conFound


def overlayPNG(imgBack, imgFront, pos=[0, 0]):

    hf, wf, cf = imgFront.shape
    hb, wb, cb = imgBack.shape

    x1, y1 = max(pos[0], 0), max(pos[1], 0)
    x2, y2 = min(pos[0] + wf, wb), min(pos[1] + hf, hb)

    # For negative positions, change the starting position in the overlay image
    x1_overlay = 0 if pos[0] >= 0 else -pos[0]
    y1_overlay = 0 if pos[1] >= 0 else -pos[1]

    # Calculate the dimensions of the slice to overlay
    wf, hf = x2 - x1, y2 - y1

    # If overlay is completely outside background, return original background
    if wf <= 0 or hf <= 0:
        return imgBack

    # Extract the alpha channel from the foreground and create the inverse mask
    alpha = imgFront[y1_overlay:y1_overlay + hf, x1_overlay:x1_overlay + wf, 3] / 255.0
    inv_alpha = 1.0 - alpha

    # Extract the RGB channels from the foreground
    imgRGB = imgFront[y1_overlay:y1_overlay + hf, x1_overlay:x1_overlay + wf, 0:3]

    # Alpha blend the foreground and background
    for c in range(0, 3):
        imgBack[y1:y2, x1:x2, c] = imgBack[y1:y2, x1:x2, c] * inv_alpha + imgRGB[:, :, c] * alpha

    return imgBack


def rotateImage(imgInput, angle, scale=1, keepSize=False):

    # Get the dimensions of the input image (height and width)
    h, w = imgInput.shape[:2]

    # Calculate the center of the original image
    center = (w / 2, h / 2)

    # Calculate the rotation matrix
    rotate_matrix = cv2.getRotationMatrix2D(center=center, angle=angle, scale=scale)

    if keepSize:
        new_w = w
        new_h = h
    else:
        # Calculate the new dimensions of the image
        abs_cos = abs(rotate_matrix[0, 0])
        abs_sin = abs(rotate_matrix[0, 1])

        new_w = int(h * abs_sin + w * abs_cos)
        new_h = int(h * abs_cos + w * abs_sin)

        # Adjust the rotation matrix to take into account the new dimensions
        rotate_matrix[0, 2] += new_w / 2 - center[0]
        rotate_matrix[1, 2] += new_h / 2 - center[1]

    # Perform the actual rotation and return the image
    imgOutput = cv2.warpAffine(src=imgInput, M=rotate_matrix, dsize=(new_w, new_h))

    return imgOutput


def putTextRect(img, text, pos, scale=3, thickness=3, colorT=(255, 255, 255),
                colorR=(255, 0, 255), font=cv2.FONT_HERSHEY_PLAIN,
                offset=10, border=None, colorB=(0, 255, 0)):

    ox, oy = pos
    (w, h), _ = cv2.getTextSize(text, font, scale, thickness)

    x1, y1, x2, y2 = ox - offset, oy + offset, ox + w + offset, oy - h - offset

    cv2.rectangle(img, (x1, y1), (x2, y2), colorR, cv2.FILLED)
    if border is not None:
        cv2.rectangle(img, (x1, y1), (x2, y2), colorB, border)
    cv2.putText(img, text, (ox, oy), font, scale, colorT, thickness)

    return img, [x1, y2, x2, y1]


def downloadImageFromUrl(url, keepTransparency=False):

    # Download the image using urllib
    url_response = urllib.request.urlopen(url)

    # Convert the downloaded bytes to a numpy array
    image_data = np.asarray(bytearray(url_response.read()), dtype=np.uint8)

    # Decode the image data
    if keepTransparency:
        image = cv2.imdecode(image_data, cv2.IMREAD_UNCHANGED)
    else:
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    return image


def main():
    cap = cv2.VideoCapture(2)

    # ------ downloadImageFromUrl ------#
    imgPNG = downloadImageFromUrl(
        url='https://github.com/cvzone/cvzone/blob/master/Results/cvzoneLogo.png?raw=true',
        keepTransparency=True)

    imgShapes = downloadImageFromUrl(
        url='https://github.com/cvzone/cvzone/blob/master/Results/shapes.png?raw=true')

    while True:
        success, img = cap.read()

        # ------ putTextRect ------- #
        img, bbox = putTextRect(img, "CVZone", (50, 50),
                                scale=3, thickness=3,
                                colorT=(255, 255, 255), colorR=(255, 0, 255),
                                font=cv2.FONT_HERSHEY_PLAIN, offset=10,
                                border=5, colorB=(0, 255, 0))
        # ------ cornerRect ------- #
        img = cornerRect(img, (200, 200, 300, 200),
                         l=30, t=5, rt=1,
                         colorR=(255, 0, 255), colorC=(0, 255, 0))

        # ------ rotateImage ------- #
        imgRotated60 = rotateImage(img, 60, scale=1, keepSize=False)
        imgRotated60KeepSize = rotateImage(img, 60, scale=1, keepSize=True)
        cv2.imshow("imgRotated60", imgRotated60)
        cv2.imshow("imgRotated60KeepSize", imgRotated60KeepSize)

        # ------ overlayPNG ------- #
        imgOverlay = overlayPNG(img, imgPNG, pos=[-30, 100])
        cv2.imshow("imgOverlay", imgOverlay)

        # ------ findContours ------- #
        imgCanny = cv2.Canny(imgShapes, 50, 150)
        imgDilated = cv2.dilate(imgCanny, np.ones((5, 5), np.uint8), iterations=1)
        imgContours, conFound = findContours(imgShapes, imgDilated, minArea=1000, sort=True,
                                             filter=None, drawCon=True, c=(255, 0, 0), ct=(255, 0, 255),
                                             retrType=cv2.RETR_EXTERNAL, approxType=cv2.CHAIN_APPROX_NONE)
        imgContoursFiltered, conFoundFiltered = findContours(imgShapes, imgDilated, minArea=1000, sort=True,
                                                             filter=[3, 4], drawCon=True, c=(255, 0, 0),
                                                             ct=(255, 0, 255),
                                                             retrType=cv2.RETR_EXTERNAL,
                                                             approxType=cv2.CHAIN_APPROX_NONE)
        cv2.imshow("imgContours", imgContours)
        cv2.imshow("imgContoursFiltered", imgContoursFiltered)

        # ------ stackImages ------- #
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgList = [img, imgGray]
        imgStacked = stackImages(imgList, 2, 0.8)
        cv2.imshow("stackedImg", imgStacked)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
