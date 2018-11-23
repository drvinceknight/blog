import pathlib
import re
import collections
import tempfile

import jinja2
import markdown
import yaml
import json

from nbconvert import HTMLExporter

ROOT = "blog"
BLOGTITLE = "Un peu de math"
DESCRIPTION = """
A blog about programming (usually scientific python), mathematics
(usually game theory) and learning (usually student centred pedagogic
approaches)."""

Post = collections.namedtuple(
    "post", ["stub", "title", "description", "date", "content", "metadata", "path"]
)


def get_stub(path):
    """
    Return the stem of a path.
    """
    date = get_date(path)
    string = str(path.parent)
    return string[string.index(date) + len("yyyy-mm-dd-"):]


def get_date(path):
    """
    Returns the date in ISO format at the start of the name of a directory
    """
    date_regex = (
        "(19|20)\d\d[- ./](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])"
    )
    try:
        return re.search(date_regex, str(path)).group()
    except AttributeError:
        return None


def get_markdown_content_and_metadata(path, delimeter="---"):
    """
    Returns the html of a given markdown file
    """
    raw = path.read_text()
    raw_metadata, md = raw[: raw.index(delimeter)], raw[raw.index(delimeter) :]
    metadata = yaml.load(raw_metadata)
    return markdown.markdown(md), metadata

def get_ipynb_content_and_metadata(path, delimeter="---"):
    """
    Returns the html of a given ipynb file
    """
    contents = path.read_text()
    nb = json.loads(contents)

    cells = []
    for cell in nb["cells"]:
        if ("tags" not in cell["metadata"] or 
            "post_metadata" not in cell["metadata"]["tags"] and
            "ignore" not in cell["metadata"]["tags"]):
            cells.append(cell)
        elif "post_metadata" in cell["metadata"]["tags"]:
            metadata = yaml.load("".join(cell["source"]))

    nb["cells"] = cells

    temporary_nb = tempfile.NamedTemporaryFile()
    with open(temporary_nb.name, "w") as f:
        f.write(json.dumps(nb))

    html_exporter = HTMLExporter()
    html_exporter.template_file = "basic"
    return html_exporter.from_file(temporary_nb)[0], metadata



def read_file(path):
    """
    Return a Post object given a path to a blog post
    """
    stub = get_stub(path)
    date = get_date(path)
    if path.suffix == ".ipynb":
        content, metadata = get_ipynb_content_and_metadata(path)
    if path.suffix == ".md":
        content, metadata = get_markdown_content_and_metadata(path)

    content = content.replace("{{root}}", ROOT)
    return Post(
        stub=stub,
        title=metadata["title"],
        description=metadata.get("description", ""),
        date=date,
        content=content,
        metadata=metadata,
        path=path,
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
            "blog_description": DESCRIPTION,
            "path": str(post.path),
            "filename": str(post.path.name),
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
    for post_path in reversed(list(src_path.glob("./*/main*"))):
        post = read_file(path=post_path)
        write_post(post=post, output_dir=output_dir)
        posts.append(post)

    html = render_template(
        "home.html",
        {
            "blog_title": BLOGTITLE,
            "posts": posts,
            "root": ROOT,
            "blog_description": DESCRIPTION,
        },
    )
    (output_dir.parent / "index.html").write_text(html)


if __name__ == "__main__":
    main()
