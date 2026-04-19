import cv2
import os
from dotenv import load_dotenv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from inference_sdk import InferenceHTTPClient
from config import MOUTH_LANDMARKS, APPLE_PTS, COOKIE_PTS, MOUTH_BOX_HEIGHT_SCALE, MOUTH_BOX_WIDTH_SCALE

load_dotenv()

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
        box_w = int(MOUTH_BOX_WIDTH_SCALE * face_h)
        box_h = int(MOUTH_BOX_HEIGHT_SCALE * face_h)

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

class SnackTrack:
    def __init__(self):
        # self.eating_frames = 0
        self.cookie_bites = 0
        self.apple_bites = 0
        self.points = 0
        # self.streak = 0

    def overlaps(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)
    
    def snack_counter(self, snack_type):
        if snack_type.lower() == "apple":
            self.apple_bites += 1
            self.points += APPLE_PTS
        else:
            self.cookie_bites += 1
            self.points += COOKIE_PTS
        
    
