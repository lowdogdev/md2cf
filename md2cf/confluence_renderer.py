import uuid
from pathlib import Path
from typing import List, NamedTuple
from urllib.parse import unquote, urlparse

import mistune
from mistune.util import escape as escape_text

from md2cf.admonition import panel_macro


class RelativeLink(NamedTuple):
    path: str
    fragment: str
    replacement: str
    original: str
    escaped_original: str


class ConfluenceTag(object):
    def __init__(self, name, text="", attrib=None, namespace="ac", cdata=False):
        self.name = name
        self.text = text
        self.namespace = namespace
        if attrib is None:
            attrib = {}
        self.attrib = attrib
        self.children = []
        self.cdata = cdata

    def render(self):
        namespaced_name = self.add_namespace(self.name, namespace=self.namespace)
        namespaced_attribs = {
            self.add_namespace(
                attribute_name, namespace=self.namespace
            ): attribute_value
            for attribute_name, attribute_value in self.attrib.items()
        }

        content = "<{}{}>{}{}</{}>".format(
            namespaced_name,
            " {}".format(
                " ".join(
                    [
                        '{}="{}"'.format(name, value)
                        for name, value in sorted(namespaced_attribs.items())
                    ]
                )
            )
            if namespaced_attribs
            else "",
            "".join([child.render() for child in self.children]),
            "<![CDATA[{}]]>".format(self.text) if self.cdata else self.text,
            namespaced_name,
        )
        return "{}\n".format(content)

    @staticmethod
    def add_namespace(tag, namespace):
        return "{}:{}".format(namespace, tag)

    def append(self, child):
        self.children.append(child)


class ConfluenceRenderer(mistune.Renderer):
    def __init__(
        self,
        strip_header=False,
        remove_text_newlines=False,
        enable_relative_links=False,
        frontmatter_attachments=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.frontmatter_attachment_names = {
            Path(attachment).name for attachment in frontmatter_attachments or []
        }
        self.strip_header = strip_header
        self.remove_text_newlines = remove_text_newlines
        self.attachments = list()
        self.title = None
        self.enable_relative_links = enable_relative_links
        self.relative_links: List[RelativeLink] = list()

    def reinit(self):
        self.attachments = list()
        self.relative_links = list()
        self.title = None

    def header(self, text, level, raw=None):
        if self.title is None and level == 1:
            self.title = text
            # Don't duplicate page title as a header
            if self.strip_header:
                return ""

        return super(ConfluenceRenderer, self).header(text, level, raw=raw)

    def structured_macro(self, name):
        return ConfluenceTag("structured-macro", attrib={"name": name})

    def parameter(self, name, value):
        parameter_tag = ConfluenceTag("parameter", attrib={"name": name})
        parameter_tag.text = value
        return parameter_tag

    def plain_text_body(self, text):
        body_tag = ConfluenceTag("plain-text-body", cdata=True)
        body_tag.text = text
        return body_tag

    def admonition(self, text, kind="note", title=""):
        root_element = self.structured_macro(panel_macro(kind))
        if title:
            root_element.append(self.parameter(name="title", value=escape_text(title)))
        body = ConfluenceTag("rich-text-body")
        body.text = text
        root_element.append(body)
        return root_element.render()

    def block_html(self, html):
        # HTML comments are for authors; Confluence should not show them.
        if html.strip().startswith("<!--"):
            return ""
        return super().block_html(html)

    def inline_html(self, html):
        if html.startswith("<!--"):
            return ""
        return super().inline_html(html)

    def table_cell(self, text, align=None, head=False):
        # In a table, "\|" stands for a literal pipe, including inside code spans.
        text = text.replace("\\|", "|")
        tag = "th" if head else "td"
        style = f' style="text-align:{align}"' if align else ""
        return f"  <{tag}{style}>{text}</{tag}>\n"

    def link(self, text, url, title=None):
        parsed_link = urlparse(url)
        if (
            self.enable_relative_links
            and (not parsed_link.scheme and not parsed_link.netloc)
            and parsed_link.path
        ):
            # relative link
            replacement_link = f"md2cf-internal-link-{uuid.uuid4()}"
            self.relative_links.append(
                RelativeLink(
                    # make sure to unquote the url as relative paths
                    # might have escape sequences
                    path=unquote(parsed_link.path),
                    replacement=replacement_link,
                    fragment=parsed_link.fragment,
                    original=link,
                    escaped_original=mistune.escape_link(link),
                )
            )
            link = replacement_link
        return super(ConfluenceRenderer, self).link(link, title, text)

    def text(self, text):
        if self.remove_text_newlines:
            text = text.replace("\n", " ")

        return super().text(text)

    def block_code(self, code, lang=None):
        root_element = self.structured_macro("code")
        if lang is not None:
            lang_parameter = self.parameter(name="language", value=lang)
            root_element.append(lang_parameter)
        root_element.append(self.parameter(name="linenumbers", value="true"))
        root_element.append(self.plain_text_body(code))
        return root_element.render()

<<<<<<< HEAD
    def image(self, src, title, text):
=======
    def drawio_diagram_name(self, url):
        name = Path(url).name
        if not name.lower().endswith(".drawio.png"):
            return None
        drawio_name = name[: -len(".png")]
        if drawio_name in self.frontmatter_attachment_names:
            return drawio_name
        return None

    def image(self, text, url, title=None):
        parsed_source = urlparse(url)
        if not parsed_source.netloc:
            diagram_name = self.drawio_diagram_name(url)
            if diagram_name:
                self.attachments.append(url)
                macro = self.structured_macro("drawio")
                macro.append(self.parameter(name="diagramName", value=diagram_name))
                macro.append(self.parameter(name="diagramDisplayName", value=diagram_name))
                return macro.render()

>>>>>>> 68e6979 (Handle admonition, drawio and replace homepage)
        attributes = {"alt": text}
        if title:
            attributes["title"] = title

        root_element = ConfluenceTag(name="image", attrib=attributes)
<<<<<<< HEAD
        parsed_source = urlparse(src)
=======
>>>>>>> 68e6979 (Handle admonition, drawio and replace homepage)
        if not parsed_source.netloc:
            # Local file, requires upload
            basename = Path(src).name
            url_tag = ConfluenceTag(
                "attachment", attrib={"filename": basename}, namespace="ri"
            )
            self.attachments.append(src)
        else:
            url_tag = ConfluenceTag("url", attrib={"value": src}, namespace="ri")
        root_element.append(url_tag)

        return root_element.render()
