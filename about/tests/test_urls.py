from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_exist_at_desired_locations(self):
        """Проверка доступности адресов страниц
        /about/author/ и /about/tech/"""
        url_templates = {
            '/about/author/',
            '/about/tech/',
        }
        for url in url_templates:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_author_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/author/."""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/tech/."""
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')
