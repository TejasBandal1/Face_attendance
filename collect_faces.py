import cv2
import os

facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

if not os.path.exists("dataset"):
    os.makedirs("dataset")

emp_id = input("Enter Employee ID: ")
name = input("Enter Name: ")

video = cv2.VideoCapture(0)
count = 0

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        count += 1
        cv2.imwrite(f"dataset/{emp_id}_{name}_{count}.jpg", face)

        cv2.putText(frame, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Collecting Faces", frame)

    if cv2.waitKey(1) == ord('q') or count >= 100:
        break

video.release()
cv2.destroyAllWindows()
print("✅ Face data collection complete!")
