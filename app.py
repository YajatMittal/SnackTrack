import json
import time
import threading
import queue
from flask import Flask, Response, jsonify, render_template, stream_with_context
import cv2

from backend.tracker import SnackTrack, StateManager
from backend.detectors import MouthDetector, SnackDetector
from backend.drawing import draw_mouth, draw_snack, draw_text
from config import EATING_FRAME_THRESHOLD, SCORE_FILE

app = Flask(__name__)

# setup
cap = cv2.VideoCapture(0)
state_manager = StateManager(SCORE_FILE)
state_manager.load_state()
mouth_detector = MouthDetector()
snack_detector = SnackDetector()
snack_tracker = SnackTrack(state_manager)

eating_frames = 0
state_lock = threading.Lock()
frame_lock = threading.Lock()
event_queue = queue.Queue(maxsize=128)
latest_frame_jpg = None  # shared between capture thread and /video route


def push_event(event):
    try:
        event_queue.put_nowait(event)
    except queue.Full:
        pass


def capture_loop():
    """Runs in background thread — handles camera, detection, state updates."""
    global eating_frames, latest_frame_jpg

    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        mouth = mouth_detector.detect(frame)
        snack = snack_detector.detect(frame)

        if mouth:
            draw_mouth(frame, mouth)
        if snack:
            draw_snack(frame, snack)

        if mouth and snack and snack_tracker.overlaps(snack["box"], mouth["box"]):
            eating_frames += 1
        else:
            eating_frames = 0

        if eating_frames == EATING_FRAME_THRESHOLD and snack:
            snack_tracker.snack_counter(snack["label"])
            last_log = state_manager.state.get("log", [])
            if last_log:
                latest_entry = last_log[-1]
                push_event({
                    "type": "score",
                    "item": snack["label"],
                    "pts": latest_entry.get("pts", 0),
                })

        # update state
        with state_lock:
            state = state_manager.state
            state["face_detected"] = bool(mouth)
            state["snack_detected"] = snack["label"] if snack else None
            state["eating"] = eating_frames >= EATING_FRAME_THRESHOLD
            state["last_item"] = snack["label"] if state["eating"] and snack else state.get("last_item")

        # encode and store latest frame
        success, jpg = cv2.imencode(".jpg", frame)
        if success:
            with frame_lock:
                latest_frame_jpg = jpg.tobytes()

        time.sleep(0.033)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video")
def video():
    def gen():
        while True:
            with frame_lock:
                jpg = latest_frame_jpg
            if jpg:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
            time.sleep(0.033)
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/state")
def get_state():
    with state_lock:
        s = state_manager.state
        return jsonify({
            "score": s["score"],
            "apples": s["apple_bites"],
            "cookies": s["cookie_bites"],
            "streak": s["healthy_streak"],
            "last_item": s.get("last_item"),
            "eating": s.get("eating", False),
            "face_detected": s.get("face_detected", False),
            "snack_detected": s.get("snack_detected"),
            "log": s["log"],
            "date": s["date"],
        })


@app.route("/events")
def events():
    def stream():
        yield "data: {\"type\":\"connected\"}\n\n"
        while True:
            try:
                ev = event_queue.get(timeout=15)
                yield f"data: {json.dumps(ev)}\n\n"
            except queue.Empty:
                yield "data: {\"type\":\"ping\"}\n\n"
    return Response(stream_with_context(stream()),
                    mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/reset", methods=["POST"])
def reset():
    with state_lock:
        state_manager.reset()
        state_manager.state["face_detected"] = False
        state_manager.state["snack_detected"] = None
        state_manager.state["eating"] = False
        state_manager.state["last_item"] = None
    return jsonify({"ok": True})


if __name__ == "__main__":
    # start camera in background thread
    t = threading.Thread(target=capture_loop, daemon=True)
    t.start()
    print("\n🎮 Snack Tracker running → http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)