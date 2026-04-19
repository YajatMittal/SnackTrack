import cv2
from detectors import MouthDetector, SnackDetector, SnackTrack
from drawing import draw_mouth, draw_snack, draw_text
 
mouth_detector = MouthDetector()
snack_detector = SnackDetector()
snack_tracker = SnackTrack()

cap = cv2.VideoCapture(0)
eating_frames = 0

while True:
    success, frame = cap.read()

    if not success:
        break
    
    draw_text(frame, f"Cookie Bites: {snack_tracker.cookie_bites}", 50, 50)
    draw_text(frame, f"Apple Bites: {snack_tracker.apple_bites}", 50, 150)
    draw_text(frame, f"Points: {snack_tracker.points}", 50, 250)

    mouth = mouth_detector.detect(frame)
    snack = snack_detector.detect(frame)
    
    if mouth:
        draw_mouth(frame, mouth)
 
    if snack:
        draw_snack(frame, snack)
 
    if mouth and snack:
        if snack_tracker.overlaps(snack["box"], mouth["box"]):
            eating_frames += 1
            
        else:
            eating_frames = 0
 
        if eating_frames == 5:
            snack_tracker.snack_counter(snack["label"])
    
        
    cv2.imshow("SnackTrack", frame)
 
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
 
cap.release()
cv2.destroyAllWindows()