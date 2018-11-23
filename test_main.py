import pathlib

import main


def test_get_stub():
    path = pathlib.Path(
        "./src/2018-07-10-just-enough-static-site-generator/main.md"
    )
    assert main.get_stub(path) == "just-enough-static-site-generator"


def test_get_date():
    path = pathlib.Path(
        "./src/2018-07-10-just-enough-static-site-generator/main.md"
    )
    assert main.get_date(path) == "2018-07-10"


def test_get_date():
    path = pathlib.Path(
        "./src/2018-07-10-just-enough-static-site-generator/main.md"
    )
    html, metadata = main.get_markdown_content_and_metadata(path)
    assert type(html) is str
    assert type(metadata) is dict


def test_read_file():
    path = pathlib.Path(
        "./src/2018-07-10-just-enough-static-site-generator/main.md"
    )
    post = main.read_file(path)
    assert type(post) is main.Post
