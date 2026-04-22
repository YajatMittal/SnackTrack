# SnackTrack 🍎

SnackTrack is a fun, real-time snack tracking application that uses computer vision to monitor your eating habits. It detects faces and mouths using MediaPipe, identifies snacks (apples or cookies) via a custom Roboflow model, and scores points based on your choices—rewarding healthy eating while playfully penalizing junk food. The app features a sleek web interface with live video feed, scoring dashboard, streaks, and activity logs.

## Features

- **Real-Time Detection**: Live camera feed with face and mouth detection using MediaPipe.
- **Snack Recognition**: Custom Roboflow model identifies apples (+15 points) and cookies (-10 points).
- **Scoring System**: Tracks daily score, healthy streaks, and snack counts.
- **Web Interface**: Modern UI with score rings, progress bars, activity feed, and toasts.
- **Data Persistence**: Saves state to JSON file, resets daily.
- **Event Streaming**: Real-time updates via Server-Sent Events (SSE).
- **Reset Functionality**: Easy daily reset button.

## Tech Stack

- **Backend**: Python with Flask, OpenCV, MediaPipe, Roboflow Inference SDK.
- **Frontend**: HTML, CSS (custom styles), JavaScript (vanilla).
- **AI/ML**: MediaPipe Face Landmarker for mouth detection; custom Roboflow model for snack classification.
- **Deployment**: Runs locally on Flask server.

## Installation

### Prerequisites

- Python >=3.10 and <3.13 (required for the latest inference-sdk versions, e.g., 0.38.0; I personally used Python 3.11 for my venv)
- Webcam (built-in or external)
- Roboflow account and API key (for snack detection)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/snacktrack.git
   cd snacktrack
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Create a `.env` file in the root directory.
   - Add your Roboflow API key:
     ```
     ROBOFLOW_API_KEY=your_api_key_here
     ```
   - Obtain the API key from your Roboflow account dashboard.

5. **Download the MediaPipe model**:
   - The `face_landmarker.task` file should be in the `backend/` directory. If missing, download from MediaPipe's official resources.

## Usage

1. **Run the application**:
   ```bash
   python backend/app.py
   ```

2. **Open your browser**:
   - Navigate to `http://localhost:5000`.
   - Grant camera permissions when prompted.

3. **Start tracking**:
   - Position your face in the camera view.
   - Hold an apple or cookie near your mouth.
   - The app will detect eating and update scores in real-time.

4. **Monitor progress**:
   - View your score, streaks, and activity log on the dashboard.
   - Reset daily data with the "↺ RESET DAY" button.

## Roboflow Model

The snack detection is powered by a custom Roboflow model I personally created and trained for distinguishing between apples and cookies. This model was trained on a dataset of images featuring these snacks in various lighting and orientations, achieving high accuracy for real-time inference.

### Why It's Helpful
- **Custom Training**: Tailored to the specific use case, reducing false positives compared to generic object detection models.
- **Real-Time Performance**: Optimized for low-latency inference via Roboflow's serverless API.
- **Extensible**: Easily adaptable for other snack types or food categories.

### Using Your Own Model
To customize SnackTrack for different snacks or improve detection:

1. **Create a Roboflow Project**:
   - Sign up at [Roboflow](https://roboflow.com).
   - Create a new project for object detection.

2. **Collect and Annotate Data**:
   - Upload images of your target snacks (e.g., apples, cookies, or others).
   - Annotate bounding boxes around the snacks using Roboflow's annotation tools.

3. **Train the Model**:
   - Use Roboflow's training interface to train a model (e.g., YOLOv8 or similar).
   - Export the model for inference.

4. **Update the Code**:
   - In `backend/detectors.py`, change the `model_id` in `SnackDetector.__init__()` to your model's ID.
   - Adjust scoring in `config.py` (e.g., add points for new snacks).
   - Update the frontend labels in `frontend/main.js` and `frontend/index.html` accordingly.

5. **Test Locally**:
   - Run the app and verify detection with your custom model.

This approach allows anyone to personalize SnackTrack for their dietary goals or expand it to track multiple food items.

## Project Structure

```
SnackTrack/
├── backend/
│   ├── app.py              # Flask server and routes
│   ├── config.py           # Constants and configuration
│   ├── detectors.py        # Mouth and snack detection classes
│   ├── drawing.py          # OpenCV drawing utilities
│   ├── tracker.py          # Scoring and state management
│   ├── face_landmarker.task # MediaPipe model file
│   └── scores.json         # Persistent state file
├── frontend/
│   ├── index.html          # Main web page
│   ├── main.js             # Frontend logic and SSE handling
│   └── style.css           # Stylesheet
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── .env                    # Environment variables (not committed)
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss your ideas.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MediaPipe for face detection.
- Roboflow for easy model deployment.
- OpenCV for computer vision utilities.
- Flask for the web framework.

Enjoy tracking your snacks responsibly! 🍎🍪
