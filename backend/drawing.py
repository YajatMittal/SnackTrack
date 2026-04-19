import cv2

def draw_mouth(frame, state: dict) -> None:
    for px, py in state["landmark_pixels"]:
        cv2.circle(frame, (px, py), 3, (255, 255, 255), -1)
    
    x1,y1,x2,y2 = state["box"]
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(frame, "Mouth", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

def draw_snack(frame, prediction: dict) -> None:
    x1, y1, x2, y2 = prediction["box"]
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(frame, prediction["label"], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

def draw_text(frame, text, x1, y1) -> None:
    cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)