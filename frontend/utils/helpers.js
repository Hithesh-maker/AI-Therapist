export function setStatus(element, message, isBusy = false) {
  element.textContent = message;
  element.classList.toggle('typing', isBusy);
}

export function mapEmotionToEmoji(emotion) {
  const map = {
    happy: '😊',
    sad: '😢',
    angry: '😠',
    surprised: '😲',
    neutral: '😐',
    fear: '😨',
    disgust: '🤢',
    confused: '😕',
    tired: '🥱',
  };

  return map[(emotion || '').toLowerCase()] || '🤖';
}
