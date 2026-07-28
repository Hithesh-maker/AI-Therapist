from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import base64
import numpy as np
import cv2
import mediapipe as mp
import os
import joblib
import gc


# ================= PATH =================

BASE_DIR = os.path.dirname(__file__)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "face_model.pkl"
)


# ================= LOAD ML MODEL =================

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        "face_model.pkl not found"
    )


model = joblib.load(MODEL_PATH)

print("✅ Face model loaded")


# ================= FLASK =================

app = Flask(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend"
)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

CORS(app, resources={r"/*": {"origins": "*"}})


# ================= MEDIAPIPE LAZY LOAD =================

face_mesh = None


def get_face_mesh():

    global face_mesh

    if face_mesh is None:

        print("Loading MediaPipe...")

        try:
            mp_face = mp.solutions.face_mesh

            face_mesh = mp_face.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=False,
                min_detection_confidence=0.5,
            )

            print("✅ MediaPipe loaded")

        except Exception as exc:
            print("⚠️ MediaPipe init failed:", exc)
            face_mesh = False

    return face_mesh


# Warm up MediaPipe once at startup so the first analyze-face request is faster.
try:
    get_face_mesh()
except Exception:
    pass



# ================= HOME =================


@app.route("/")
def home():

    return render_template(
        "index.html"
    )



# ================= FACE API =================


@app.route("/predict", methods=["POST"])
def predict():
    try:
        print("========== NEW REQUEST ==========")

        data = request.get_json()

        if not data:
            print("No JSON")
            return jsonify({"error": "No JSON"}), 400

        print("JSON received")

        image = data.get("image")

        if not image:
            print("No image")
            return jsonify({"error": "No image"}), 400

        if "," in image:
            image = image.split(",")[1]

        print("Decoding base64...")

        img_bytes = base64.b64decode(image)

        print("Converting numpy...")

        np_img = np.frombuffer(img_bytes, np.uint8)

        print("Decoding image...")

        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img is None:
            print("Image decode failed")
            return jsonify({"error": "Invalid image"}), 400

        print("Resizing...")

        img = cv2.resize(img, (320, 240))

        print("Converting RGB...")

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        print("Loading MediaPipe...")

        mesh = get_face_mesh()

        print("Running FaceMesh...")

        results = mesh.process(rgb)

        print("FaceMesh finished")

        if not results.multi_face_landmarks:
            print("No face detected")
            return jsonify({
                "emotion": "No Face",
                "score": 0
            })

        print("Extracting landmarks...")

        landmarks = []

        for point in results.multi_face_landmarks[0].landmark:
            landmarks.extend([point.x, point.y, point.z])

        print("Creating feature vector...")

        features = np.array(landmarks).reshape(1, -1)

        print("Running model.predict()...")

        prediction = model.predict(features)[0]

        confidence = 0

        if hasattr(model, "predict_proba"):
            confidence = int(
                max(model.predict_proba(features)[0]) * 100
            )

        print("Prediction complete")

        del img
        del rgb
        del results
        gc.collect()

        return jsonify({
            "emotion": str(prediction),
            "score": confidence
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

    

# ================= VOICE =================


@app.route(

    "/predict_voice",

    methods=["POST"]

)

def predict_voice():


    try:


        audio=request.files.get(
            "audio"
        )


        if not audio:


            return jsonify({

                "error":"No audio"

            }),400



        return jsonify({

            "emotion":"neutral",

            "confidence":90

        })



    except Exception as e:


        return jsonify({

            "error":str(e)

        }),500




# ================= RUN =================


if __name__=="__main__":


    app.run(

        host="0.0.0.0",

        port=5000

    )