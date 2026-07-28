class WebcamService {
  constructor(videoElement) {
    this.videoElement = videoElement;
    this.stream = null;
  }

  async start() {
    if (this.stream) return this.stream;
    this.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    this.videoElement.srcObject = this.stream;
    this.videoElement.play();
    return this.stream;
  }

  stop() {
    if (!this.stream) return;
    this.stream.getTracks().forEach((track) => track.stop());
    this.stream = null;
  }
}

export default WebcamService;
