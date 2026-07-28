from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

import base64
import numpy as np
import cv2
import mediapipe as mp
import os
import joblib


# ================= LOAD MODEL =================

BASE_DIR = os.path.dirname(__file__)

model_path = os.path.join(
    BASE_DIR,
    "models",
    "face_model.pkl"
)


if not os.path.exists(model_path):
    raise FileNotFoundError(
        "face_model.pkl missing"
    )


model = joblib.load(model_path)

print("✅ Face model loaded")


# ================= FLASK =================


app = Flask(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend"
)


CORS(app)



# ================= MEDIAPIPE =================


mp_face = mp.solutions.face_mesh


face_mesh = mp_face.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)



# ================= HOME =================


@app.route("/")
def home():

    return render_template(
        "index.html"
    )



# ================= FACE PREDICTION =================


@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        print("📸 Face request received")


        data = request.get_json()


        if not data or "image" not in data:

            return jsonify({
                "error":"No image"
            }),400



        image = data["image"]


        # remove base64 header

        encoded = image.split(",")[1]


        img_bytes = base64.b64decode(
            encoded
        )


        np_img = np.frombuffer(
            img_bytes,
            np.uint8
        )


        img = cv2.imdecode(
            np_img,
            cv2.IMREAD_COLOR
        )



        if img is None:

            return jsonify({
                "error":"Invalid image"
            }),400



        # IMPORTANT FOR RENDER RAM

        img = cv2.resize(
            img,
            (320,240)
        )



        rgb = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )



        results = face_mesh.process(
            rgb
        )



        if not results.multi_face_landmarks:


            print(
                "No face found"
            )


            return jsonify({

                "emotion":
                "No Face",

                "score":
                0

            })



        landmarks=[]


        for point in results.multi_face_landmarks[0].landmark:

            landmarks.extend([
                point.x,
                point.y,
                point.z
            ])



        features=np.array(
            landmarks
        ).reshape(
            1,-1
        )



        expected = model.n_features_in_


        if features.shape[1] != expected:


            print(
                "Feature mismatch",
                features.shape[1],
                expected
            )


            return jsonify({

                "emotion":
                "Invalid Features",

                "score":
                0

            })



        prediction = model.predict(
            features
        )[0]


        score = 0


        if hasattr(model,"predict_proba"):

            score = int(
                max(
                    model.predict_proba(features)[0]
                )*100
            )



        print(
            "Prediction:",
            prediction,
            score
        )


        return jsonify({

            "emotion":
            str(prediction),

            "score":
            score

        })



    except Exception as e:


        print(
            "FACE ERROR:",
            e
        )


        return jsonify({

            "error":
            str(e)

        }),500





# ================= VOICE =================


@app.route(
    "/predict_voice",
    methods=["POST"]
)

def voice():


    try:


        audio=request.files.get(
            "audio"
        )


        if not audio:


            return jsonify({

                "error":
                "No audio"

            }),400



        return jsonify({

            "emotion":
            "neutral",

            "confidence":
            90

        })


    except Exception as e:


        return jsonify({

            "error":
            str(e)

        }),500





# ================= START =================


if __name__=="__main__":


    app.run(
        host="0.0.0.0",
        port=5000
    )