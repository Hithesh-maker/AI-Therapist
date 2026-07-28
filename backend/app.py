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

                "error":"No image received"

            }),400



        image=data["image"]



        if "," in image:

            image=image.split(",")[1]



        img_bytes = base64.b64decode(
            image
        )


        np_img=np.frombuffer(

            img_bytes,

            np.uint8

        )


        img=cv2.imdecode(

            np_img,

            cv2.IMREAD_COLOR

        )



        if img is None:

            return jsonify({

                "error":"Invalid image"

            }),400



        # reduce size

        img=cv2.resize(

            img,

            (320,240)

        )



        rgb=cv2.cvtColor(

            img,

            cv2.COLOR_BGR2RGB

        )



        mesh=get_face_mesh()



        results=mesh.process(
            rgb
        )



        if not results.multi_face_landmarks:


            print("⚠ No face")


            return jsonify({

                "emotion":"No Face",

                "score":0

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



        if features.shape[1] != model.n_features_in_:


            print(

                "Feature mismatch",

                features.shape[1],

                model.n_features_in_

            )


            return jsonify({

                "emotion":"Invalid Features",

                "score":0

            })



        prediction=model.predict(

            features

        )[0]



        confidence=0



        if hasattr(

            model,

            "predict_proba"

        ):


            confidence=int(

                max(

                    model.predict_proba(features)[0]

                )*100

            )



        print(

            "🎯",

            prediction,

            confidence

        )



        # clear memory

        del img

        del rgb

        del results

        gc.collect()



        return jsonify({

            "emotion":str(prediction),

            "score":confidence

        })



    except Exception as e:


        print(

            "❌ FACE ERROR",

            e

        )


        return jsonify({

            "error":str(e)

        }),500




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