import sounddevice as sd
import soundfile as sf
import librosa
import numpy as np
import os
import csv

# Settings
duration = 3  # seconds
sample_rate = 22050

# CSV file for features
if not os.path.exists('voice_data.csv'):
    file = open('voice_data.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(['mfcc_' + str(i) for i in range(40)] + ['label'])
else:
    file = open('voice_data.csv', 'a', newline='')
    writer = csv.writer(file)

print("📢 Press 1:Happy  2:Sad  3:Angry  4:Neutral  | q:Quit")

label_map = {
    '1': 'happy',
    '2': 'sad',
    '3': 'angry',
    '4': 'neutral'
}

while True:
    cmd = input("Select Emotion (1/2/3/4/q): ").strip()

    if cmd.lower() == 'q':
        break

    if cmd not in label_map:
        continue

    print(f"🎙️ Recording {label_map[cmd]}... Speak now!")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()

    # Extract MFCCs
    mfccs = librosa.feature.mfcc(y=recording.flatten(), sr=sample_rate, n_mfcc=40)
    mfccs_mean = np.mean(mfccs, axis=1)

    # Save to CSV
    writer.writerow(list(mfccs_mean) + [label_map[cmd]])
    print(f"✅ Saved {label_map[cmd]} sample.")

file.close()
print("📁 Data saved to voice_data.csv")
