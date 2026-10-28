"""Support for MkDocs / Python-Markdown admonitions.

    !!! note "Optional title"
        Body text, indented by four spaces. The body is ordinary Markdown.

Each admonition is rendered as a Confluence panel macro (info, tip, note or warning).
"""
import re

HEADER = r'^!!! +(?P<kind>[A-Za-z]+)(?: +"(?P<title>[^"\n]*)")?[ \t]*(?:\n|$)'

# Admonition type to Confluence macro name. Unknown types fall back to an info panel.
PANELS = {
    "note": "info",
    "info": "info",
    "abstract": "info",
    "summary": "info",
    "tip": "tip",
    "hint": "tip",
    "success": "tip",
    "warning": "warning",
    "caution": "warning",
    "attention": "warning",
    "danger": "warning",
    "error": "warning",
    "failure": "warning",
    "bug": "warning",
}


def parse_admonition(block, m, state):
    kind = m.group("kind").lower()
    title = m.group("title") or ""

    pos = m.end()
    lines = []
    while pos < state.cursor_max:
        line = state.get_line(pos)
        if line.startswith("    "):
            lines.append(line[4:])
        elif not line.strip():
            lines.append("\n")
        else:
            break
        pos += len(line)

    body = "".join(lines).strip("\n")
    child = state.child_state(body + "\n" if body else "")
    block.parse(child)
    state.append_token(
        {
            "type": "admonition",
            "children": child.tokens,
            "attrs": {"kind": kind, "title": title},
        }
    )
    return pos


def admonition(md):
    """mistune plugin: parse `!!! kind "title"` blocks."""
    md.block.register("admonition", HEADER, parse_admonition, before="paragraph")
    # The renderer method is defined on ConfluenceRenderer.


def panel_macro(kind):
    return PANELS.get(kind, "info")

