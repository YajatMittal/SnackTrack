import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# load the model
base_options = python.BaseOptions(model_asset_path="face_landmarker.task")

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_faces=1
)

landmarker = vision.FaceLandmarker.create_from_options(options) 

MOUTH_LANDMARKS = [
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409,
    291, 375, 321, 405, 314, 17, 84, 181, 91, 146,
    61,78, 191, 80, 81, 82, 13, 312, 311, 310, 415,
    308, 324, 318, 402, 317, 14, 87, 178, 88, 95,
    78
]

# webcam
cap = cv2.VideoCapture(0)

def draw_mouth_landmarks(face, frame, w, h):
    for landmark in MOUTH_LANDMARKS:
        landmark_mouth = face[landmark]
        px = int(landmark_mouth.x * w)
        py = int(landmark_mouth.y * h)
        cv2.circle(frame, (px, py), 3, (255, 255, 255), -1)

def get_face_height(face, h):
    return abs(face[152].y - face[10].y) * h

def check_mouth_state(face, w, h):
        landmark_upperlip = face[13]
        landmark_lowerlip = face[14]
        
        px_upper = int(landmark_upperlip.x * w)
        py_upper = int(landmark_upperlip.y * h)
        px_lower = int(landmark_lowerlip.x * w)
        py_lower = int(landmark_lowerlip.y * h)

        distance = abs(py_upper-py_lower)

        face_h = get_face_height(face, h)
        state = (distance / face_h) > 0.07
        
        box_w = int(0.32 * face_h)
        box_h = int(0.15 * face_h)
        
        return (state, px_upper, py_upper, px_lower, py_lower, box_h, box_w)



while True:
    success, frame = cap.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result = landmarker.detect(mp_image)
    
    if result.face_landmarks:
        face = result.face_landmarks[0]
        h, w, _ = frame.shape
        draw_mouth_landmarks(face, frame, w, h)
        state, px_upper, py_upper, px_lower, py_lower, box_h, box_w = check_mouth_state(face, w, h)

        #determining mouth center
        mouth_x = int((px_upper + px_lower) / 2)
        mouth_y = int((py_upper + py_lower) / 2)

        x1 = mouth_x - box_w
        y1 = mouth_y - box_h
        x2 = mouth_x + box_w
        y2 = mouth_y + box_h  
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if state:
            label = "open"  
        else:
            label = "closed"
        
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imshow("SnackTrack", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
