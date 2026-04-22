from flask import Flask, Response, jsonify, render_template
from backend.tracker import StateManager
from config import SCORE_FILE

app = Flask(__name__)
state_manager = StateManager(SCORE_FILE)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video")
def video():
    pass

@app.route("/state")
def get_state():
    return jsonify(state_manager.state)


@app.route("/events")

@app.route("/reset", methods=["POST"])
def reset():
    state_manager.reset()
    return jsonify({"ok": True})

if __name__ == "__main__":
    print("\n🎮 Snack Tracker running \n")
    app.run(debug=True)
