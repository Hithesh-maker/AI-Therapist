class ApiService {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  async request(path, options = {}) {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: { Accept: 'application/json', ...(options.headers || {}) },
      ...options,
    });

    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
      throw new Error(typeof payload === 'string' ? payload : payload.error || 'Request failed');
    }

    return payload;
  }

  async health() {
    return this.request('/health');
  }

  async predictFace(payload) {
    return this.request('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  async predictVoice(formData) {
    return this.request('/predict_voice', {
      method: 'POST',
      body: formData,
    });
  }
}

export default ApiService;
