from html import escape
from html.parser import HTMLParser

from django import template
from django.utils.html import urlize
from django.utils.safestring import mark_safe


register = template.Library()


class _HtmlAutoLinkParser(HTMLParser):
    """Auto-link text nodes without altering existing HTML tags or attributes."""

    _skip_tags = {"a", "script", "style"}

    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        self._parts.append(self._render_start_tag(tag, attrs, self_closing=False))
        if tag in self._skip_tags:
            self._skip_depth += 1

    def handle_startendtag(self, tag, attrs):
        self._parts.append(self._render_start_tag(tag, attrs, self_closing=True))

    def handle_endtag(self, tag):
        self._parts.append(f"</{tag}>")
        if tag in self._skip_tags and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth:
            self._parts.append(data)
            return
        self._parts.append(urlize(data, autoescape=True))

    def handle_entityref(self, name):
        self._parts.append(f"&{name};")

    def handle_charref(self, name):
        self._parts.append(f"&#{name};")

    def handle_comment(self, data):
        self._parts.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self._parts.append(f"<!{decl}>")

    def unknown_decl(self, data):
        self._parts.append(f"<![{data}]>")

    def get_html(self):
        return "".join(self._parts)

    @staticmethod
    def _render_start_tag(tag, attrs, self_closing):
        rendered_attrs = []
        for key, value in attrs:
            if value is None:
                rendered_attrs.append(f" {key}")
            else:
                rendered_attrs.append(f' {key}="{escape(value, quote=True)}"')

        closing = " />" if self_closing else ">"
        return f"<{tag}{''.join(rendered_attrs)}{closing}"


@register.filter(name="autolink_html")
def autolink_html(value):
    if not value:
        return ""

    parser = _HtmlAutoLinkParser()
    parser.feed(str(value))
    parser.close()
    return mark_safe(parser.get_html())
