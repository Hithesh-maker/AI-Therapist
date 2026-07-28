from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import base64
import io
import numpy as np
import cv2
import mediapipe as mp
import os
import joblib
import wave

# ------------------- Load Model -------------------
model_path = os.path.join(os.path.dirname(__file__), 'models', 'face_model.pkl')

if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ face_model.pkl not found at {model_path}")

model = joblib.load(model_path)
print(f"✅ Loaded Model from {model_path}")

# ------------------- Flask App Setup -------------------
app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')
CORS(app, resources={r"/*": {"origins": "*"}})

# ------------------- MediaPipe FaceMesh -------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5
)

# ------------------- Routes -------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_emotion():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.json.get('image')
        if not data:
            return jsonify({'error': 'No image data received'}), 400

        header, encoded = data.split(',', 1) if ',' in data else ('', data)
        if not encoded:
            return jsonify({'error': 'Invalid image data'}), 400

        image_data = base64.b64decode(encoded)
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Unable to decode image'}), 400

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_img)

        if not results.multi_face_landmarks:
            print("⚠️ No face detected.")
            return jsonify({'emotion': 'No Face Detected', 'score': 0})

        face = results.multi_face_landmarks[0]
        landmarks = []
        for lm in face.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])

        if len(landmarks) != model.n_features_in_:
            print(f"⚠️ Landmark shape mismatch: Expected {model.n_features_in_}, got {len(landmarks)}")
            return jsonify({'emotion': 'Invalid Face Data', 'score': 0})

        landmarks_np = np.array(landmarks).reshape(1, -1)
        prediction = model.predict(landmarks_np)[0]
        confidence = model.predict_proba(landmarks_np)[0].max()

        print(f"🎯 Predicted: {prediction} | Confidence: {confidence:.2f}")

        return jsonify({
            'emotion': prediction,
            'score': int(confidence * 100)
        })

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({'error': str(e)}), 500


@app.route('/predict_voice', methods=['POST'])
def predict_voice():
    try:
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({'error': 'No audio data received'}), 400

        audio_bytes = audio_file.read()
        if not audio_bytes:
            return jsonify({'error': 'Empty audio data'}), 400

        audio_buffer = io.BytesIO(audio_bytes)
        with wave.open(audio_buffer, 'rb') as wav_file:
            frames = wav_file.readframes(wav_file.getnframes())

        if not frames:
            return jsonify({'emotion': 'No audio detected', 'confidence': 0})

        return jsonify({
            'emotion': 'neutral',
            'confidence': 100
        })

    except Exception as e:
        print("❌ Voice Error:", e)
        return jsonify({'error': str(e)}), 500

# ------------------- Run App -------------------
if __name__ == '__main__':
    app.run(debug=True)
