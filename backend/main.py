import cv2
from detectors import MouthDetector, SnackDetector, overlaps
from drawing import draw_mouth, draw_snack, draw_eating
 
mouth_detector = MouthDetector()
snack_detector = SnackDetector()
eating_frames = 0

cap = cv2.VideoCapture(0)
eating_frames = 0

while True:
    success, frame = cap.read()

    if not success:
        break
    
    mouth = mouth_detector.detect(frame)
    snack = snack_detector.detect(frame)
    
    if mouth:
        draw_mouth(frame, mouth)
 
    if snack:
        draw_snack(frame, snack)
 
    if mouth and snack:
        if overlaps(snack["box"], mouth["box"]):
            eating_frames += 1
        else:
            eating_frames = 0
 
        if eating_frames > 5:
            draw_eating(frame)
        
    cv2.imshow("SnackTrack", frame)
 
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
 
cap.release()
cv2.destroyAllWindows()