import io
import unittest

from backend.app import app


class BackendApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_predict_returns_json_error_for_missing_image(self):
        response = self.client.post('/predict', json={})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertIn('error', payload)

    def test_predict_voice_route_exists(self):
        response = self.client.post(
            '/predict_voice',
            data={'audio': (io.BytesIO(b'fake-audio-data'), 'audio.wav')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('emotion', payload)
        self.assertIn('confidence', payload)


if __name__ == '__main__':
    unittest.main()
