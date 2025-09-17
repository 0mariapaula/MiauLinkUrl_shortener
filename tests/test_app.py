import unittest
from main import app

class UrlShortenerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MiauLink', response.data)

    def test_url_shorten_and_redirect(self):
        # Cria uma URL encurtada
        response = self.app.post('/', data={'url': 'https://www.exemplo.com'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Encurtada', response.data)

        # Extrai o código da URL encurtada
        import re
        match = re.search(rb'/([a-zA-Z0-9]{6})', response.data)
        self.assertIsNotNone(match)
        code = match.group(1).decode()

        # Testa o redirecionamento
        redirect_response = self.app.get(f'/{code}', follow_redirects=False)
        self.assertEqual(redirect_response.status_code, 302)
        self.assertIn('https://www.exemplo.com', redirect_response.headers['Location'])

if __name__ == '__main__':
    unittest.main()
