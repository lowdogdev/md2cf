from pathlib import Path

import pytest

from md2cf import __main__ as cli
from md2cf.api import Bunch
from md2cf.document import Page


def parse_args(*argv):
    return cli.get_parser().parse_args(list(argv))


@pytest.fixture()
def space_info():
    return Bunch({"homepage": {"id": "999"}})


def test_replace_homepage_defaults_to_none():
    assert parse_args("docs").replace_homepage is None


def test_replace_homepage_takes_a_path_and_combines_with_top_level():
    args = parse_args("--top-level", "--replace-homepage", "docs/index.md", "docs")

    assert args.replace_homepage == Path("docs/index.md")
    assert args.top_level is True
    assert args.file_list == [Path("docs")]


def test_pre_process_homepage_page_targets_space_homepage(space_info):
    args = parse_args(
        "-s", "S", "--top-level", "--prefix", "P", "--replace-homepage", "docs/index.md"
    )
    page = Page(
        title="HCCP Documentation", body="", file_path=Path("docs/index.md")
    )

    cli.pre_process_page(page, args, "", "", space_info)

    assert page.page_id == "999"
    assert page.parent_id is None
    assert page.parent_title is None
    assert page.title == "HCCP Documentation"


def test_pre_process_homepage_ignores_parent_title(space_info):
    args = parse_args("--top-level", "--replace-homepage", "docs/index.md")
    page = Page(
        title="Home",
        body="",
        file_path=Path("docs/index.md"),
        parent_title="folder",
    )

    cli.pre_process_page(page, args, "", "", space_info)

    assert page.page_id == "999"
    assert page.parent_title is None
    assert page.parent_id is None


def test_pre_process_other_pages_are_unchanged(space_info):
    args = parse_args(
        "--top-level", "--prefix", "P", "--replace-homepage", "docs/index.md"
    )
    page = Page(title="Other", body="", file_path=Path("docs/other/index.md"))

    cli.pre_process_page(page, args, "", "", space_info)

    assert page.page_id is None
    assert page.parent_id == "999"
    assert page.title == "P - Other"


def test_pre_process_without_flag_is_unchanged(space_info):
    args = parse_args("--top-level")
    page = Page(title="Index", body="", file_path=Path("docs/index.md"))

    cli.pre_process_page(page, args, "", "", space_info)

    assert page.page_id is None
    assert page.parent_id == "999"


def test_collect_homepage_already_in_directory_is_not_duplicated(fs):
    fs.create_file("/docs/index.md", contents="# Home\n")
    fs.create_file("/docs/a/index.md", contents="# A\n")
    args = parse_args("--replace-homepage", "/docs/index.md", "/docs")

    pages = cli.collect_pages_to_upload(args)

    assert [p.file_path for p in pages].count(Path("/docs/index.md")) == 1


def test_collect_homepage_outside_file_list_is_added(fs):
    fs.create_file("/docs/index.md", contents="# Home\n")
    fs.create_file("/docs/a/index.md", contents="# A\n")
    fs.create_file("/docs/b/index.md", contents="# B\n")
    args = parse_args(
        "--replace-homepage", "/docs/index.md", "/docs/a", "/docs/b"
    )

    pages = cli.collect_pages_to_upload(args)

    assert pages[0].file_path == Path("/docs/index.md")
    assert pages[0].title == "Home"
    assert len(pages) == 3


def test_collect_homepage_added_with_relative_links_enabled(fs):
    fs.create_file(
        "/docs/index.md", contents="# Home\n\n[a](a/index.md)\n"
    )
    fs.create_file("/docs/a/index.md", contents="# A\n")
    args = parse_args(
        "--enable-relative-links", "--replace-homepage", "/docs/index.md", "/docs/a"
    )

    pages = cli.collect_pages_to_upload(args)

    homepage = pages[0]
    assert homepage.file_path == Path("/docs/index.md")
    assert len(homepage.relative_links) == 1


def test_collect_homepage_alone_does_not_read_stdin(fs):
    fs.create_file("/docs/index.md", contents="# Home\n")
    args = parse_args("--replace-homepage", "/docs/index.md")

    pages = cli.collect_pages_to_upload(args)

    assert [p.file_path for p in pages] == [Path("/docs/index.md")]


def test_collect_missing_homepage_file_exits(fs):
    fs.create_file("/docs/a/index.md", contents="# A\n")
    args = parse_args("--replace-homepage", "/docs/index.md", "/docs/a")

    with pytest.raises(SystemExit):
        cli.collect_pages_to_upload(args)
