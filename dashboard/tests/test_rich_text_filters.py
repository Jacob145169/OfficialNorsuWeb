from django.template import Context, Template
from django.test import SimpleTestCase


class AutoLinkHtmlFilterTests(SimpleTestCase):
    def render(self, content):
        template = Template("{% load rich_text %}{{ content|autolink_html }}")
        return template.render(Context({"content": content}))

    def test_plain_text_urls_become_clickable_inside_html(self):
        rendered = self.render(
            "<p>Register here:</p><p>https://example.com/form?foo=1&amp;bar=2</p>"
        )

        self.assertIn('<a href="https://example.com/form?foo=1&amp;bar=2">', rendered)
        self.assertIn("<p>Register here:</p>", rendered)

    def test_existing_html_attributes_and_links_stay_intact(self):
        rendered = self.render(
            '<p><a href="https://example.com">Existing link</a></p>'
            '<p><img src="https://cdn.example.com/photo.png" alt="Poster"></p>'
            '<p>Visit https://openai.com for details.</p>'
        )

        self.assertIn('<a href="https://example.com">Existing link</a>', rendered)
        self.assertIn('src="https://cdn.example.com/photo.png"', rendered)
        self.assertIn('<a href="https://openai.com">https://openai.com</a>', rendered)
        self.assertEqual(rendered.count("<a href="), 2)
