import cv2

cap = cv2.VideoCapture(0)

# providing the path to the model
FACE_DETECTION_MODEL = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

while True:
    success, frame = cap.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_DETECTION_MODEL.detectMultiScale(gray_frame, 1.3, 5)

    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (225,0,0), 4)
        cv2.putText(frame, "Face", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.9, (36,255,12), 2)

    cv2.imshow("SnackTrack", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()