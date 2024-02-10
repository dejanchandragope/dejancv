
import cv2
import numpy as np
import tensorflow


class Classifier:

    def __init__(self, modelPath, labelsPath=None):

        self.model_path = modelPath
        np.set_printoptions(suppress=True)  # Disable scientific notation for clarity

        # Load the Keras model
        self.model = tensorflow.keras.models.load_model(self.model_path)

        # Create a NumPy array with the right shape to feed into the Keras model
        self.data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        self.labels_path = labelsPath

        # If a labels file is provided, read and store the labels
        if self.labels_path:
            label_file = open(self.labels_path, "r")
            self.list_labels = [line.strip() for line in label_file]
            label_file.close()
        else:
            print("No Labels Found")

    def getPrediction(self, img, draw=True, pos=(50, 50), scale=2, color=(0, 255, 0)):

        # Resize and normalize the image
        imgS = cv2.resize(img, (224, 224))
        image_array = np.asarray(imgS)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the data array
        self.data[0] = normalized_image_array

        # Run inference
        prediction = self.model.predict(self.data)
        indexVal = np.argmax(prediction)

        # Draw the prediction text on the image if specified
        if draw and self.labels_path:
            cv2.putText(img, str(self.list_labels[indexVal]), pos, cv2.FONT_HERSHEY_COMPLEX, scale, color, 2)

        return list(prediction[0]), indexVal


if __name__ == "__main__":
    cap = cv2.VideoCapture(2)  # Initialize video capture
    path = "C:/Users/USER/Documents/maskModel/"
    maskClassifier = Classifier(f'{path}/keras_model.h5', f'{path}/labels.txt')

    while True:
        _, img = cap.read()  # Capture frame-by-frame
        prediction = maskClassifier.getPrediction(img)
        print(prediction)  # Print prediction result
        cv2.imshow("Image", img)
        cv2.waitKey(1)  # Wait for a key press
