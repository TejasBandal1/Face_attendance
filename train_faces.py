import cv2
import os
import numpy as np
import pickle

facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

dataset_path = "dataset"
faces, labels = [], []
label_map, label_id = {}, 0

for filename in os.listdir(dataset_path):
    if filename.endswith(".jpg"):
        img = cv2.imread(os.path.join(dataset_path, filename), cv2.IMREAD_GRAYSCALE)

        emp_id, name, _ = filename.split("_", 2)  # Split only first 2 parts
        key = f"{emp_id}_{name}"

        if key not in label_map:
            label_map[key] = (label_id, emp_id, name)
            label_id += 1

        faces.append(img)
        labels.append(label_map[key][0])

faces = np.array(faces)
labels = np.array(labels)

recognizer.train(faces, labels)
recognizer.write("data/face_model.yml")

# Save label map {label_id: (emp_id, name)}
with open("data/label_map.pkl", "wb") as f:
    pickle.dump(label_map, f)

print("✅ Training complete. Model saved!")
