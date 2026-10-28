from pathlib import Path

import md2cf.document as doc
from test_package.utils import FakePage

ROOT_GITIGNORE = """.git
"""


def test_page_get_content_hash():
    p = doc.Page(title="test title", body="test content")

    assert p.get_content_hash() == "1eebdf4fdc9fc7bf283031b93f9aef3338de9052"


def test_get_pages_from_directory(fs):
    fs.create_file("/root-folder/root-folder-file.md")
    fs.create_dir("/root-folder/empty-dir")
    fs.create_file("/root-folder/parent/child/child-file.md")

    result = doc.get_pages_from_directory(Path("/root-folder"))
    assert result == [
        FakePage(
            title="root-folder-file",
            file_path=Path("/root-folder/root-folder-file.md", parent_title=None),
        ),
        FakePage(title="parent", file_path=None, parent_title=None),
        FakePage(title="child", file_path=None, parent_title="parent"),
        FakePage(
            title="child-file",
            file_path=Path("/root-folder/parent/child/child-file.md"),
            parent_title="child",
        ),
    ]


def test_get_pages_from_directory_use_pages(fs):
    fs.create_file("/root-folder/.gitignore", contents=ROOT_GITIGNORE)
    fs.create_dir("/root-folder/.git")
    fs.create_dir("/root-folder/.git/refs")
    fs.create_file("/root-folder/.git/refs/test.md")
    fs.create_file("/root-folder/root-folder-file.md")
    fs.create_dir("/root-folder/empty-dir")
    fs.create_file("/root-folder/parent/child/child-file.md")

    result = doc.get_pages_from_directory(
        Path("/root-folder"), use_pages_file=True, enable_relative_links=True
    )
    print(result)
    assert result == [
        FakePage(
            title="root-folder-file",
            file_path=Path("/root-folder/root-folder-file.md", parent_title=None),
        ),
        FakePage(title="parent", file_path=None, parent_title=None),
        FakePage(title="child", file_path=None, parent_title="parent"),
        FakePage(
            title="child-file",
            file_path=Path("/root-folder/parent/child/child-file.md"),
            parent_title="child",
        ),
    ]


def test_get_pages_from_directory_collapse_single_pages(fs):
    fs.create_file("/root-folder/root-folder-file.md")
    fs.create_file("/root-folder/parent/child/child-file.md")

    result = doc.get_pages_from_directory(
        Path("/root-folder"), collapse_single_pages=True
    )
    assert result == [
        FakePage(
            title="root-folder-file",
            file_path=Path("/root-folder/root-folder-file.md", parent_title=None),
        ),
        FakePage(title="parent", file_path=None, parent_title=None),
        FakePage(
            title="child-file",
            file_path=Path("/root-folder/parent/child/child-file.md"),
            parent_title="parent",
        ),
    ]


def test_get_pages_from_directory_collapse_single_pages_no_non_empty_parent(fs):
    fs.create_file("/root-folder/parent/child/child-file.md")

    result = doc.get_pages_from_directory(
        Path("/root-folder"), collapse_single_pages=True
    )
    assert result == [
        FakePage(
            title="parent",
        ),
        FakePage(
            title="child-file",
            file_path=Path("/root-folder/parent/child/child-file.md"),
            parent_title="parent",
        ),
    ]


def test_get_pages_from_directory_skip_empty(fs):
    fs.create_file("/root-folder/root-folder-file.md")
    fs.create_file("/root-folder/parent/child/child-file.md")

    result = doc.get_pages_from_directory(Path("/root-folder"), skip_empty=True)
    assert result == [
        FakePage(
            title="root-folder-file",
            file_path=Path("/root-folder/root-folder-file.md", parent_title=None),
        ),
        FakePage(
            title="child",
            file_path=None,
            parent_title=None,
        ),
        FakePage(
            title="child-file",
            file_path=Path("/root-folder/parent/child/child-file.md"),
            parent_title="child",
        ),
    ]


def test_get_pages_from_directory_skip_empty_no_non_empty_parent(fs):
    fs.create_file("/root-folder/parent/child/child-file.md")

    result = doc.get_pages_from_directory(Path("/root-folder"), skip_empty=True)
    assert result == [
        FakePage(
            title="child",
            file_path=None,
            parent_title=None,
        ),
        FakePage(
            title="child-file",
            file_path=Path("/root-folder/parent/child/child-file.md"),
            parent_title="child",
        ),
    ]


def test_get_pages_from_directory_collapse_empty(fs):
    fs.create_file("/root-folder/root-folder-file.md")
    fs.create_file("/root-folder/parent/child/child-file.md")

    result = doc.get_pages_from_directory(Path("/root-folder"), collapse_empty=True)
    assert result == [
        FakePage(
            title="root-folder-file",
            file_path=Path("/root-folder/root-folder-file.md", parent_title=None),
        ),
        FakePage(
            title="parent/child",
            file_path=None,
            parent_title=None,
        ),
        FakePage(
            title="child-file",
            file_path=Path("/root-folder/parent/child/child-file.md"),
            parent_title="parent/child",
        ),
    ]


def test_get_pages_from_directory_collapse_empty_no_non_empty_parent(fs):
    fs.create_file("/root-folder/parent/child/child-file.md")

    result = doc.get_pages_from_directory(Path("/root-folder"), collapse_empty=True)
    assert result == [
        FakePage(
            title="parent/child",
            file_path=None,
            parent_title=None,
        ),
        FakePage(
            title="child-file",
            file_path=Path("/root-folder/parent/child/child-file.md"),
            parent_title="parent/child",
        ),
    ]


def test_get_pages_from_directory_beautify_folders(fs):
    fs.create_file("/root-folder/ugly-folder/another_yucky_folder/child-file.md")

    result = doc.get_pages_from_directory(Path("/root-folder"), beautify_folders=True)
    assert result == [
        FakePage(
            title="Ugly folder",
        ),
        FakePage(
            title="Another yucky folder",
        ),
        FakePage(
            title="child-file",
            file_path=Path(
                "/root-folder/ugly-folder/another_yucky_folder/child-file.md"
            ),
            parent_title="Another yucky folder",
        ),
    ]


def test_get_pages_from_directory_with_pages_file_multi_level(fs):
    fs.create_file("/root-folder/sub-folder-a/some-page.md")
    fs.create_file("/root-folder/sub-folder-b/some-page.md")
    fs.create_file("/root-folder/sub-folder-a/.pages", contents='title: "Folder A"')
    fs.create_file("/root-folder/sub-folder-b/.pages", contents='title: "Folder B"')

    result = doc.get_pages_from_directory(Path("/root-folder"), use_pages_file=True)
    assert result == [
        FakePage(
            title="Folder A",
        ),
        FakePage(
            title="some-page",
            file_path=Path("/root-folder/sub-folder-a/some-page.md"),
            parent_title="Folder A",
        ),
        FakePage(
            title="Folder B",
        ),
        FakePage(
            title="some-page",
            file_path=Path("/root-folder/sub-folder-b/some-page.md"),
            parent_title="Folder B",
        ),
    ]


def test_get_pages_from_directory_with_pages_file_single_level(fs):
    fs.create_file("/root-folder/some-page.md")
    fs.create_file("/root-folder/.pages", contents='title: "Root folder"')

    result = doc.get_pages_from_directory(Path("/root-folder"), use_pages_file=True)
    assert result == [
        FakePage(
            title="Root folder",
        ),
        FakePage(
            title="some-page",
            file_path=Path("/root-folder/some-page.md"),
            parent_title="Root folder",
        ),
    ]


def test_get_document_frontmatter():
    source_markdown = """---
title: This is a title
labels:
  - label1
  - label2
---
# This is normal markdown content

Yep.
"""

    assert doc.get_document_frontmatter(source_markdown.splitlines(keepends=True)) == {
        "title": "This is a title",
        "labels": ["label1", "label2"],
        "frontmatter_end_line": 6,
    }


def test_get_document_frontmatter_only_first():
    source_markdown = """---
title: This is a title
---
# This is normal markdown content

---

With other triple dashes!

Yep.
"""

    assert doc.get_document_frontmatter(source_markdown.splitlines(keepends=True)) == {
        "title": "This is a title",
        "frontmatter_end_line": 3,
    }


def test_get_document_frontmatter_no_closing():
    source_markdown = """---
# This is normal markdown content

Yep.
"""

    assert doc.get_document_frontmatter(source_markdown.splitlines(keepends=True)) == {}


def test_get_document_frontmatter_extra_whitespace():
    source_markdown = """

---
title: This is a title
---
# This is normal markdown content

Yep.
"""

    assert doc.get_document_frontmatter(source_markdown.splitlines(keepends=True)) == {}


def test_get_document_frontmatter_empty():
    source_markdown = """---
---
# This is normal markdown content

Yep.
"""

    assert doc.get_document_frontmatter(source_markdown.splitlines(keepends=True)) == {}


def parse(markdown):
    return doc.get_page_data_from_lines(markdown.splitlines(keepends=True)).body


def test_pipe_table_is_rendered_as_a_table():
    body = parse("| A | B |\n| --- | --- |\n| 1 | 2 |\n")

    assert "<table>" in body
    assert "<th>A</th>" in body
    assert "<td>2</td>" in body
    assert "| --- |" not in body


def test_table_with_empty_header_cells_is_rendered_as_a_table():
    body = parse("| | |\n| --- | --- |\n| **Key** | value |\n")

    assert "<table>" in body
    assert "<strong>Key</strong>" in body


def test_escaped_pipe_in_a_table_cell_is_a_literal_pipe():
    body = parse("| A |\n| --- |\n| `a\\|b` |\n")

    assert "<code>a|b</code>" in body


def test_table_column_alignment():
    body = parse("| A | B |\n| :--- | ---: |\n| 1 | 2 |\n")

    assert '<th style="text-align:left">A</th>' in body
    assert '<td style="text-align:right">2</td>' in body


def test_strikethrough():
    assert "<del>gone</del>" in parse("some ~~gone~~ text\n")


def test_admonition_becomes_an_info_panel_with_a_title():
    body = parse('!!! note "A title"\n    Some **text**.\n')

    assert '<ac:structured-macro ac:name="info">' in body
    assert '<ac:parameter ac:name="title">A title</ac:parameter>' in body
    assert "<ac:rich-text-body><p>Some <strong>text</strong>.</p>" in body
    assert "!!!" not in body


def test_admonition_without_a_title():
    body = parse("!!! warning\n    Careful.\n")

    assert '<ac:structured-macro ac:name="warning">' in body
    assert "ac:name=\"title\"" not in body


def test_admonition_title_is_escaped():
    body = parse('!!! note "Fish & <chips>"\n    text\n')

    assert "Fish &amp; &lt;chips&gt;" in body


def test_admonition_body_can_contain_lists_tables_and_blank_lines():
    body = parse(
        '!!! note "T"\n'
        "    First paragraph.\n"
        "\n"
        "    - one\n"
        "    - two\n"
        "\n"
        "    | h |\n"
        "    | - |\n"
        "    | 1 |\n"
    )

    assert body.count("<ac:structured-macro") == 1
    assert "<ul>" in body and "<li>one</li>" in body
    assert "<table>" in body


def test_text_after_an_admonition_is_outside_the_panel():
    body = parse('!!! note "T"\n    inside\n\noutside\n')

    inside, _, after = body.partition("</ac:structured-macro>")
    assert "inside" in inside
    assert "<p>outside</p>" in after


def test_unknown_admonition_type_falls_back_to_an_info_panel():
    assert 'ac:name="info"' in parse('!!! whatever "T"\n    text\n')


def test_two_admonitions_in_a_row():
    body = parse('!!! note "One"\n    a\n\n!!! warning "Two"\n    b\n')

    assert body.count("<ac:structured-macro") == 2
    assert 'ac:name="info"' in body and 'ac:name="warning"' in body


def test_admonition_header_is_not_mistaken_for_text_in_a_code_block():
    body = parse("```\n!!! note\n    text\n```\n")

    assert "<ac:structured-macro ac:name=\"code\">" in body
    assert 'ac:name="info"' not in body


def parse_page_with_frontmatter(markdown):
    return doc.get_page_data_from_lines(markdown.splitlines(keepends=True))


def test_png_with_drawio_in_frontmatter_renders_drawio_macro():
    page = parse_page_with_frontmatter(
        "---\nattachments:\n  - images/diagram.drawio\n  - images/diagram.drawio.png\n---\n"
        "![alt](images/diagram.drawio.png)\n"
    )

    assert '<ac:structured-macro ac:name="drawio">' in page.body
    assert (
        '<ac:parameter ac:name="diagramName">diagram.drawio</ac:parameter>'
        in page.body
    )
    assert (
        '<ac:parameter ac:name="diagramDisplayName">diagram.drawio</ac:parameter>'
        in page.body
    )
    assert "<ac:image" not in page.body
    assert page.attachments == [
        "images/diagram.drawio.png",
        "images/diagram.drawio",
        "images/diagram.drawio.png",
    ]


def test_png_without_frontmatter_still_renders_an_image():
    page = parse_page_with_frontmatter("![alt](images/diagram.drawio.png)\n")

    assert "<ac:image" in page.body
    assert 'ac:name="drawio"' not in page.body


def test_frontmatter_attachments_must_be_a_list_before_rendering():
    import pytest

    with pytest.raises(TypeError):
        parse_page_with_frontmatter(
            "---\nattachments: diagram.drawio\n---\n![alt](diagram.png)\n"
        )


def test_html_comment_block_is_dropped():
    body = parse("before\n\n<!-- hidden -->\n\nafter\n")

    assert "hidden" not in body and "&lt;" not in body
    assert "<p>before</p>" in body and "<p>after</p>" in body


def test_inline_html_comment_is_dropped():
    assert "hidden" not in parse("some <!-- hidden --> text\n")
