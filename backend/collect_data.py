import cv2
import mediapipe as mp
import sounddevice as sd
import numpy as np
import csv
import wave
import os
from datetime import datetime

# === FaceMesh Setup ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# === Voice Recording Setup ===
SAMPLE_RATE = 16000
DURATION = 3  # seconds

# === Create Directories ===
os.makedirs('voice_samples', exist_ok=True)

# === Timestamped CSV Filename ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
face_data_file = open(f'face_data_{timestamp}.csv', 'w', newline='')
face_writer = csv.writer(face_data_file)

# === Label Mapping ===
label_map = {
    ord('1'): 'happy',
    ord('2'): 'sad',
    ord('3'): 'angry',
    ord('4'): 'neutral',
}

# === Initialize Webcam ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

if not cap.isOpened():
    print("❌ Cannot open webcam.")
    exit()

print("📸 Press 1:happy 2:sad 3:angry 4:neutral | q:quit")
sample_count = 0

# === Main Loop ===
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read frame.")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    coords = None
    face_detected = False

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            face_detected = True
            mp_drawing.draw_landmarks(
                frame, landmarks, mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
            )
            coords = []
            for lm in landmarks.landmark:
                coords.extend([lm.x, lm.y, lm.z])

    msg = "1:happy 2:sad 3:angry 4:neutral | q:quit"
    msg += f" | Samples: {sample_count}"
    msg += " | ✅ Face Detected" if face_detected else " | ❌ No Face"

    cv2.putText(frame, msg, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
    cv2.imshow("AI Therapist Data Collector", frame)

    key = cv2.waitKey(1)

    if key in label_map and coords:
        label = label_map[key]
        # Save face data
        face_writer.writerow(coords + [label])

        # Record voice sample
        print(f"🎙️ Recording voice sample for {label}...")
        audio_data = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
        sd.wait()

        # Save voice file
        voice_filename = f'voice_samples/{label}_{sample_count}_{timestamp}.wav'
        with wave.open(voice_filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())

        print(f"✅ Saved sample #{sample_count}: {label}")
        sample_count += 1

    elif key == ord('q'):
        break

cap.release()
face_data_file.close()
cv2.destroyAllWindows()

print(f"📁 Face data saved to face_data_{timestamp}.csv")
print(f"📁 Voice samples saved in /voice_samples/")
