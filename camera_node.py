import face_recognition
import cv2
import os
import datetime

# Load known faces
known_face_encodings = []
known_face_names = []

for filename in os.listdir("known_faces"):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        path = os.path.join("known_faces", filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])

# Setup webcam
video = cv2.VideoCapture(0)
print("[INFO] Camera started. Press 'q' to quit.")

while True:
    ret, frame = video.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]  # BGR to RGB

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "INTRUDER"

        if True in matches:
            name = known_face_names[matches.index(True)]

        # Scale face coordinates back to original size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw label and box
        color = (0, 255, 0) if name != "INTRUDER" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Save intruder snapshot
        if name == "INTRUDER":
            if not os.path.exists("intruders"):
                os.makedirs("intruders")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            intruder_path = f"intruders/intruder_{timestamp}.jpg"
            cv2.imwrite(intruder_path, frame)

    # Display the output
    cv2.imshow("COEP Gate Camera", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
