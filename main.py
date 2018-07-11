import pathlib
import re
import collections

import jinja2
import markdown
import yaml

ROOT = "blog"
BLOGTITLE = "Un peu de math"
DESCRIPTION = """
A blog about programming (usually scientific python), mathematics
(usually game theory) and learning (usually student centred pedagogic
approaches)."""

Post = collections.namedtuple(
    "post", ["stub", "title", "description", "date", "content", "metadata"]
)


def get_stub(path):
    """
    Return the stem of a path.
    """
    return path.stem[len("yyyy-mm-dd-") :]


def get_date(path):
    """
    Returns the date in ISO format at the start of the name of a directory
    """
    date_regex = "(19|20)\d\d[- ./](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])"
    try:
        return re.search(date_regex, path.stem[: len("yyyy-mm-dd")]).group()
    except AttributeError:
        return None


def get_content_and_metadata(path, delimeter="---"):
    """
    Returns the html of a given markdown file
    """
    raw = path.read_text()
    raw_metadata, md = raw[: raw.index(delimeter)], raw[raw.index(delimeter) :]
    metadata = yaml.load(raw_metadata)
    return markdown.markdown(md), metadata


def read_file(path):
    """
    Return a Post object given a path to a blog post
    """
    stub = get_stub(path)
    date = get_date(path)
    content, metadata = get_content_and_metadata(path)
    content = content.replace("{{root}}", ROOT)
    return Post(
        stub=stub,
        title=metadata["title"],
        description=metadata.get("description", ""),
        date=date,
        content=content,
        metadata=metadata,
    )


def render_template(template_file, template_vars, searchpath="./templates/"):
    """
    Render a jinja2 template
    """
    templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
    template_env = jinja2.Environment(loader=templateLoader)
    template = template_env.get_template(template_file)
    return template.render(template_vars)


def write_post(post, output_dir):
    """
    Create the output directory and write the post
    """
    output_path = output_dir / f"{post.stub}"
    output_path.mkdir(exist_ok=True)
    html = render_template(
        "post.html",
        {
            "blog_title": BLOGTITLE,
            "description": post.description,
            "content": post.content,
            "date": post.date,
            "title": post.title,
            "root": ROOT,
        },
    )

    (output_path / "index.html").write_text(html)


def main(src_path=None, output_dir=None):
    """
    Read all the source directories
    """
    if src_path is None:
        src_path = pathlib.Path("./src/")

    if output_dir is None:
        output_dir = pathlib.Path("./posts")

    output_dir.mkdir(exist_ok=True)

    posts = []
    for post_path in reversed(list(src_path.glob("*.md"))):
        post = read_file(path=post_path)
        write_post(post=post, output_dir=output_dir)
        posts.append(post)

    html = render_template(
        "home.html",
        {
            "blog_title": BLOGTITLE,
            "posts": posts,
            "root": ROOT,
            "description": DESCRIPTION,
        },
    )
    (output_dir.parent / "index.html").write_text(html)


if __name__ == "__main__":
    main()
