import time
import cv2
import cvzone

class FPS:

    def __init__(self, avgCount=30):

        self.pTime = time.time()  # Initialize previous time to current time
        self.frameTimes = []  # List to store the time taken for each frame
        self.avgCount = avgCount  # Number of frames to average over

    def update(self, img=None, pos=(20, 50), bgColor=(255, 0, 255),
               textColor=(255, 255, 255), scale=3, thickness=3):

        cTime = time.time()  # Get the current time
        frameTime = cTime - self.pTime  # Calculate the time difference between the current and previous frame
        self.frameTimes.append(frameTime)  # Append the time difference to the list
        self.pTime = cTime  # Update previous time

        # Remove the oldest frame time if the list grows beyond avgCount
        if len(self.frameTimes) > self.avgCount:
            self.frameTimes.pop(0)

        avgFrameTime = sum(self.frameTimes) / len(self.frameTimes)  # Calculate the average frame time
        fps = 1 / avgFrameTime  # Calculate FPS based on the average frame time

        # Draw FPS on image if img is provided
        if img is not None:
            cvzone.putTextRect(img, f'FPS: {int(fps)}', pos,
                               scale=scale, thickness=thickness, colorT=textColor,
                               colorR=bgColor, offset=10)
        return fps, img



if __name__ == "__main__":
    # Initialize the FPS class with an average count of 30 frames for smoothing
    fpsReader = FPS(avgCount=30)

    # Initialize the webcam and set it to capture at 60 FPS
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 30)  # Set the frames per second to 30

    # Main loop to capture frames and display FPS
    while True:
        # Read a frame from the webcam
        success, img = cap.read()

        # Update the FPS counter and draw the FPS on the image
        # fpsReader.update returns the current FPS and the updated image
        fps, img = fpsReader.update(img, pos=(20, 50),
                                    bgColor=(255, 0, 255), textColor=(255, 255, 255),
                                    scale=3, thickness=3)

        # Display the image with the FPS counter
        cv2.imshow("Image", img)

        # Wait for 1 ms to show this frame, then continue to the next frame
        cv2.waitKey(1)