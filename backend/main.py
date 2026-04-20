import cv2
from detectors import MouthDetector, SnackDetector
from drawing import draw_mouth, draw_snack, draw_text
from config import EATING_FRAME_THRESHOLD, SCORE_FILE
from tracker import SnackTrack, StateManager
cap = cv2.VideoCapture(0)

eating_frames = 0

mouth_detector = MouthDetector()
snack_detector = SnackDetector()
state_manager = StateManager(SCORE_FILE)

state_manager.load_state()
snack_tracker = SnackTrack(state_manager)


while True:
    success, frame = cap.read()

    if not success:
        break

    draw_text(frame, f"Cookie Bites: {state_manager.state['cookie_bites']}", (50, 50))
    draw_text(frame, f"Apple Bites: {state_manager.state['apple_bites']}", (50, 100))
    draw_text(frame, f"Score: {state_manager.state['score']}", (50, 150))
    draw_text(frame, f"Healthy Streak: {state_manager.state['healthy_streak']}", (50, 200))

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

        if eating_frames == EATING_FRAME_THRESHOLD:
            snack_tracker.snack_counter(snack["label"])
        
    cv2.imshow("SnackTrack", frame)
 
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
 
cap.release()
cv2.destroyAllWindows()