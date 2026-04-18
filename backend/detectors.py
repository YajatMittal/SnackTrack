import cv2
import os
from dotenv import load_dotenv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from inference_sdk import InferenceHTTPClient

load_dotenv()

MOUTH_LANDMARKS = [
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409,
    291, 375, 321, 405, 314, 17, 84, 181, 91, 146,
    61,78, 191, 80, 81, 82, 13, 312, 311, 310, 415,
    308, 324, 318, 402, 317, 14, 87, 178, 88, 95,
    78
]

def overlaps(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

class MouthDetector:
    def __init__(self, model_path="face_landmarker.task"):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

    def detect(self, frame):
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.landmarker.detect(mp_image)

        if not result.face_landmarks:
            return None
            
        face = result.face_landmarks[0]
        
        # lip landmarks
        upper_lip = face[13]
        lower_lip = face[14]
        
        # upper and lower lip landmark pixels
        px_upper = int(upper_lip.x * w)
        py_upper = int(upper_lip.y * h)
        px_lower = int(lower_lip.x * w)
        py_lower = int(lower_lip.y * h)

        # finding face height
        face_h = abs(face[152].y - face[10].y) * h
        
        # determining bounding box width and height for mouth based on face height
        box_w = int(0.32 * face_h)
        box_h = int(0.15 * face_h)

        # determining mouth center
        mouth_x = (px_upper + px_lower) // 2
        mouth_y = (py_upper + py_lower) // 2

        landmark_pixels = [
                    (int(face[landmark].x * w), int(face[landmark].y * h))
                    for landmark in MOUTH_LANDMARKS
                ]
        
        return {
            "landmark_pixels": landmark_pixels,
            "box": (mouth_x - box_w, mouth_y - box_h, mouth_x + box_w, mouth_y + box_h),
        }        
        
class SnackDetector:
    def __init__(self, model_id="snack-detection-ypprq/2"):
        self._client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=os.getenv("ROBOFLOW_API_KEY"),
        )
        self._model_id = model_id      
    
    def detect(self, frame):
        predictions = self._client.infer(frame, model_id=self._model_id)["predictions"]
        
        if not predictions:
            return None
        
        prediction = predictions[0]
        x_cen, y_cen, w, h = int(prediction["x"]), int(prediction["y"]), int(prediction["width"]), int(prediction["height"])
       
        x1 = int(x_cen - w / 2)
        y1 = int(y_cen - h / 2)
        x2 = int(x_cen + w / 2)
        y2 = int(y_cen + h / 2)
  
        return {
            "label": prediction["class"],
            "box": (x1, y1, x2, y2),
        }