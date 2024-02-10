
import cv2
import mediapipe as mp
import math


class FaceMeshDetector:

    def __init__(self, staticMode=False, maxFaces=2, minDetectionCon=0.5, minTrackCon=0.5):

        self.staticMode = staticMode
        self.maxFaces = maxFaces
        self.minDetectionCon = minDetectionCon
        self.minTrackCon = minTrackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpFaceMesh = mp.solutions.face_mesh
        self.faceMesh = self.mpFaceMesh.FaceMesh(static_image_mode=self.staticMode,
                                                 max_num_faces=self.maxFaces,
                                                 min_detection_confidence=self.minDetectionCon,
                                                 min_tracking_confidence=self.minTrackCon)
        self.drawSpec = self.mpDraw.DrawingSpec(thickness=1, circle_radius=2)

    def findFaceMesh(self, img, draw=True):

        self.imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.faceMesh.process(self.imgRGB)
        faces = []
        if self.results.multi_face_landmarks:
            for faceLms in self.results.multi_face_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, faceLms, self.mpFaceMesh.FACEMESH_CONTOURS,
                                               self.drawSpec, self.drawSpec)
                face = []
                for id, lm in enumerate(faceLms.landmark):
                    ih, iw, ic = img.shape
                    x, y = int(lm.x * iw), int(lm.y * ih)
                    face.append([x, y])
                faces.append(face)
        return img, faces

    def findDistance(self,p1, p2, img=None):

        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            return length,info, img
        else:
            return length, info


def main():
    # Initialize the webcam
    # '2' indicates the third camera connected to the computer, '0' would usually refer to the built-in webcam
    cap = cv2.VideoCapture(0)

    # Initialize FaceMeshDetector object
    # staticMode: If True, the detection happens only once, else every frame
    # maxFaces: Maximum number of faces to detect
    # minDetectionCon: Minimum detection confidence threshold
    # minTrackCon: Minimum tracking confidence threshold
    detector = FaceMeshDetector(staticMode=False, maxFaces=2, minDetectionCon=0.5, minTrackCon=0.5)

    # Start the loop to continually get frames from the webcam
    while True:
        # Read the current frame from the webcam
        # success: Boolean, whether the frame was successfully grabbed
        # img: The current frame
        success, img = cap.read()

        # Find face mesh in the image
        # img: Updated image with the face mesh if draw=True
        # faces: Detected face information
        img, faces = detector.findFaceMesh(img, draw=True)

        # Check if any faces are detected
        if faces:
            # Loop through each detected face
            for face in faces:
                # Get specific points for the eye
                # leftEyeUpPoint: Point above the left eye
                # leftEyeDownPoint: Point below the left eye
                leftEyeUpPoint = face[159]
                leftEyeDownPoint = face[23]

                # Calculate the vertical distance between the eye points
                # leftEyeVerticalDistance: Distance between points above and below the left eye
                # info: Additional information (like coordinates)
                leftEyeVerticalDistance, info = detector.findDistance(leftEyeUpPoint, leftEyeDownPoint)

                # Print the vertical distance for debugging or information
                print(leftEyeVerticalDistance)

        # Display the image in a window named 'Image'
        cv2.imshow("Image", img)

        # Wait for 1 millisecond to check for any user input, keeping the window open
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
