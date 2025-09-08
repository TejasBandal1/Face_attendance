import cv2
import os
import csv
import time
from datetime import datetime
import pickle
from win32com.client import Dispatch

def speak(text):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

# Ensure Attendance folder exists
if not os.path.exists("Attendance"):
    os.makedirs("Attendance")

# Load model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("data/face_model.yml")

with open("data/label_map.pkl", "rb") as f:
    label_map = pickle.load(f)

# Reverse map: {label_id: (emp_id, name)}
id_to_info = {v[0]: (v[1], v[2]) for v in label_map.values()}

facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
video = cv2.VideoCapture(0)

# CSV Columns
COL_NAMES = ['EMP_ID', 'NAME', 'CHECK_IN', 'CHECK_OUT', 'TOTAL_TIME']

# Track active sessions
login_times = {}

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    current_emp_id, current_name = None, "Not Recognized"

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        label, confidence = recognizer.predict(face)

        if confidence < 50:  # Good match
            emp_id, name = id_to_info[label]
            current_emp_id, current_name = emp_id, name

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.putText(frame, f"{current_name}", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    # Instructions
    cv2.putText(frame, "Press O: Check-In | Press X: Check-Out | Q: Quit",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Attendance System", frame)
    k = cv2.waitKey(1)

    ts = time.time()
    date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
    timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    file_path = f"Attendance/Attendance_{date}.csv"

    if current_emp_id is not None:
        # ✅ Check-In
        if k == ord('o') or k == ord('O'):
            login_times[current_emp_id] = ts
            speak(f"Check-In marked for {current_name}")

            exist = os.path.isfile(file_path)
            with open(file_path, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                if not exist:
                    writer.writerow(COL_NAMES)
                writer.writerow([current_emp_id, current_name, timestamp, "", ""])

        # ✅ Check-Out
        if k == ord('x') or k == ord('X'):
            if current_emp_id in login_times:
                login_time = login_times[current_emp_id]
                logout_time = ts
                total_time = int(logout_time - login_time)  # in seconds
                hrs, rem = divmod(total_time, 3600)
                mins, secs = divmod(rem, 60)
                worked = f"{hrs:02}:{mins:02}:{secs:02}"

                speak(f"Check-Out marked for {current_name}")

                # Update last open session (where CHECK_OUT == "")
                temp_rows = []
                updated = False
                with open(file_path, "r") as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        if (row and row[0] == current_emp_id and row[3] == "" and not updated):
                            row[3] = timestamp  # CHECK_OUT
                            row[4] = worked    # TOTAL_TIME
                            updated = True
                        temp_rows.append(row)

                with open(file_path, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(temp_rows)

                del login_times[current_emp_id]

    if k == ord('q') or k == ord('Q'):
        break

video.release()
cv2.destroyAllWindows()
