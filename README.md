# Offline AI Therapist

A clean reorganized version of the AI Therapist project. This repository contains the backend Flask app, frontend UI, trained model, and dataset artifacts needed to run the application.

## Setup
1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the backend:
   ```powershell
   python backend\app.py
   ```
4. Open the browser at:
   ```text
   http://127.0.0.1:5000/
   ```

## Project structure
- `backend/`: Flask backend application and supporting scripts
- `frontend/`: Browser UI and static assets
- `backend/models/`: Trained model files
- `dataset/`: Training dataset artifacts
- `tests/`: Placeholder for future automated tests
- `.gitignore`: Excludes environment, caches, and generated files
- `render.yaml`: Render deployment configuration

## Notes
- Do not remove `backend/models/face_model.pkl`; it is required to predict face emotion.
- The existing app code is preserved exactly and should continue to work after reorganization.
- `dataset/face_data.csv` contains training data only and is kept for future model retraining.
