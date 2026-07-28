import ApiService from './services/api.js';
import WebcamService from './services/webcam.js';
import VoiceService from './services/voice.js';
import { mapEmotionToEmoji, setStatus } from './utils/helpers.js';

const api = new ApiService('');
const video = document.getElementById('webcam');
const output = document.getElementById('output');
const faceEmotionPanel = document.getElementById('faceEmotionPanel');
const faceEmotionText = document.getElementById('faceEmotionText');
const faceEmojiDisplay = document.getElementById('faceEmojiDisplay');
const voiceEmotionPanel = document.getElementById('voiceEmotionPanel');
const voiceEmotionText = document.getElementById('voiceEmotionText');
const voiceEmojiDisplay = document.getElementById('voiceEmojiDisplay');
const voiceStatus = document.getElementById('voiceStatus');
const faceButton = document.getElementById('faceButton');
const voiceButton = document.getElementById('voiceButton');
const enableCameraButton = document.getElementById('enableCameraButton');

const webcam = new WebcamService(video);
const voice = new VoiceService();

async function init() {
  try {
    await api.health();
  } catch (error) {
    setStatus(output, `Backend unavailable: ${error.message}`, false);
  }
}

async function enableCamera() {
  try {
    await webcam.start();
    setStatus(output, 'Webcam ready. Click Analyze Face to begin.', false);
  } catch (error) {
    setStatus(output, `Webcam unavailable: ${error.message}`, false);
  }
}

async function analyzeFace() {
  if (!faceButton || faceButton.disabled) return;
  faceButton.disabled = true;
  setStatus(output, 'Analyzing face...', true);

  try {
    const canvas = document.createElement('canvas');
    canvas.width = 320;
    canvas.height = 240;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const image = canvas.toDataURL('image/jpeg', 0.8);

    const data = await api.predictFace({ image });
    faceEmotionText.textContent = `${data.emotion || 'Unknown'} (Score: ${data.score ?? 'N/A'}%)`;
    faceEmojiDisplay.textContent = mapEmotionToEmoji(data.emotion);
    faceEmotionPanel.style.display = 'block';
    setStatus(output, 'Face analysis complete.', false);
  } catch (error) {
    setStatus(output, `Face analysis failed: ${error.message}`, false);
  } finally {
    faceButton.disabled = false;
  }
}

async function analyzeVoice() {
  if (!voiceButton || voiceButton.disabled) return;
  voiceButton.disabled = true;
  setStatus(voiceStatus, 'Recording voice...', false);

  try {
    const stream = await webcam.start();
    await voice.startRecording(stream);
    setTimeout(async () => {
      const blob = await voice.stopRecording();
      const formData = new FormData();
      formData.append('audio', blob, 'audio.wav');
      const data = await api.predictVoice(formData);
      voiceEmotionText.textContent = `${data.emotion || 'Unknown'} (Confidence: ${data.confidence ?? 'N/A'}%)`;
      voiceEmojiDisplay.textContent = mapEmotionToEmoji(data.emotion);
      voiceEmotionPanel.style.display = 'block';
      setStatus(voiceStatus, 'Voice analysis complete.', false);
      voiceButton.disabled = false;
    }, 3000);
  } catch (error) {
    setStatus(voiceStatus, `Voice analysis failed: ${error.message}`, false);
    voiceButton.disabled = false;
  }
}

faceButton?.addEventListener('click', analyzeFace);
voiceButton?.addEventListener('click', analyzeVoice);
enableCameraButton?.addEventListener('click', enableCamera);

window.addEventListener('DOMContentLoaded', init);
