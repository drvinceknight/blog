title: Just enough static site generator
description: A description of a small python script as a static site generator
---

I am a huge fan of static site generators. There are a number of fantastic
static site generators around: [jekyll](https://jekyllrb.com/) being one of the
most used as it renders static files hosted via
[github pages](https://pages.github.com/). Jekyll is written in
[Ruby](https://www.ruby-lang.org/en/) (a language I do not know at all) an there
are a number of others, including many written in Python (I language I do know).
On a number of occasions I've found myself not quite entirely happy with the
various options and recently I've started just writing a short Python script to
act that does the same job. In this post I'll describe the **relatively** few
lines of Python required to make a static site generator.

**TLDR** All you need to create a static site generator is a small number of
lightweight and awesome Python libraries. Here is the full file I'm about to
describe [`main.py`]({{root}}/main.py).

### What is a static site generator?

First things first: whilst most of the web is now powered by server based sites
that take a request, access a database and serve the corresponding html on the
fly a static site generator is used to do a one off read of all source files
(the "data base") and generate all the html in one go.

Most of these will for example, use the popular file format
[`markdown`](https://daringfireball.net/projects/markdown/syntax) to write blog
posts and convert them to html.

As an example this blog post is written in markdown and is currently in a file
in a directory called `src`:

    |
    |---src/
        |---2018-07-10-just-enough-static-site-generator.md

The first few lines of this file look like:

    title: Just enough static site generator
    description: A description of a small python script as a static site generator
    ---

    I am a huge fan of static site generators. There are a number of fantastic
    static site generators around: [jekyll](https://jekyllrb.com/) being one of the
    most used as it renders static files hosted via
    [github pages](https://pages.github.com/). Jekyll is written in
    [Ruby](https://www.ruby-lang.org/en/) (a language I do not know at all) an there
    are a number of others, including many written in Python (I language I do know).
    On a number of occasions I've found myself not quite entirely happy with the
    various options and recently I've started just writing a short Python script to
    act that does the same job. In this post I'll describe the **relatively** few
    lines of Python required to make a static site generator.

    **TLDR** All you need to create a static site generator is a small number of
    lightweight and awesome Python libraries. Here is the full file I'm about to
    describe [`main.py`]({{root}}/main.py).

    ### What is a static site generator?

    First things first: whilst most of the web is now powered by server based sites

**The first thing we need to be able to do is find all those files**

### Using `Pathlib` to find all the markdown files

[`Pathlib`](https://docs.python.org/3/library/pathlib.html) is a fantastic
library that provide an abstraction to file systems (so things work on \*nix and
Windows for example).

We can use `Pathlib` to easily find all the `.md` files in the `src` directory.
Here is the first step of a python function `main` that does this, it
essentially boils down to the `src_path.glob("*.md")` part.

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

You can see that there are two other functions being called inside the `for`
loop:

- `read_file`
- `write_post`

**Let us next look at reading in a given markdown file with `read_file`.**


### Using `pyyaml` and `markdown` to read and convert markdown files to html

There are two stages to this `read_file` function:

1. Getting all the information out of a `md` file.
2. Putting it all together in a nice handy format.

So here's what the `read_file` function looks like:

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

The `get_stub` and `get_date` function just read directly from the file name
which is now forced to always be of the form `<date>-<stub>.md`:

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

All of that just makes use of the `Pathlib` library but where things get
interesting is the ability to get the preamble material at the top of a markdown
file (technically speaking this is usually in a format called
[`yaml`](https://en.wikipedia.org/wiki/YAML)). Here is the
`get_content_and_metadata` function that does this:

    def get_content_and_metadata(path, delimeter="---"):
        """
        Returns the html of a given markdown file
        """
        raw = path.read_text()
        raw_metadata, md = raw[:raw.index(delimeter)], raw[raw.index(delimeter):]
        metadata = yaml.load(raw_metadata)
        return markdown.markdown(md), metadata

The first step is to split the file on the `delimeter` (`---`) which will be
used to separate the `yaml` and `md` content. Then we use the `pyyaml` library
to transform the `yaml` in to a python dictionary and the `markdown` library to
transform the rest in to html.

The last step of the `read_post` function is to return a `Post` instance. This
is just a `namedtuple` which makes things simpler to manage at a later stage:

    Post = collections.namedtuple(
        "post", ["stub", "title", "description", "date", "content", "metadata"]
    )

**Next we write this html to files that will actually be accessed/read online**

### Using `jinja2` to template how our site will look

The next part of the `main` function shown previously is to call the
`write_post` function. This makes use of the very versatile `jinja2` library
which makes using templates (so that we only need to write the structure of
pages once) straightforward. `jinja2` is actually used by a number of other
libraries but here we're using it "raw":


    def write_post(post, output_dir):
        """
        Create the output directory and write the post
        """
        output_path = output_dir / f"./{post.stub}"
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


This function takes a `Post` instance (the named tuple shown before) and an
output directory (I'll be using `posts` in my case) and then calls
`render_template` which is where `jinja2` passes the information
`post.content`, `post.date` etc to a template file `post.html`.

Here is what `render_tempalte` looks like:

    def render_template(template_file, template_vars, searchpath="./templates/"):
        """
        Render a jinja2 template
        """
        templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
        template_env = jinja2.Environment(loader=templateLoader)
        template = template_env.get_template(template_file)
        return template.render(template_vars)


The `post.html` `jinja2` template looks like:

    {% extends "base.html" %}


    {% block body %}
    <h2> {{title}} </h2>
    <h3> {{date}} </h3>

    {{content}}

    {% endblock %}

This is "extending" the `base.html` template where I've put a number of other
things including css styling.

The final part of `main.py` just passes all posts to another template
`home.html` which aims to create the [landing page]({{root}}) of this blog post:

    {% extends "base.html" %}

    {% block body %}

    <ul>
        {% for post in posts %}
        <li> <a href="/{{root}}/posts/{{post.stub}}">
                {{post.title}}</a> - {{post.date}} 
            <p>{{post.description}}</p>
        </li>
        {% endfor %}
    </ul>

    {% endblock %}

### Setting some details

The first few lines of the python file with all these functions in them has the
imports and a few global variable settings:

    import pathlib
    import re
    import collections

    import jinja2
    import markdown
    import yaml

    ROOT = "blog"
    BLOGTITLE = "Un peu de math"
    DESCRIPTION = """
    A blog about programming (usually scientific python), mathematics (game theory)
    and learning (usually student centred pedagogic approaches)."""

**Now we can render the site.**

### Building the site and serving it locally thanks to the `http` library

To render the site we simply run [`main.py`](/{{root}}/main.py):

    $ python main.py

This will create a number of `html` files in specific directories.

If you want to see this site locally on your computer, python comes with a handy
server right out of the box. Go to the parent directy and run it:

    $ cd ..
    $ python -m http.server

Then go to your browser and type in `http://localhost:8000/`, you should see a
number of directories there that should include the blog site too. Click on that
and you get a nicely rendered webpage. Of course, because this site is entirely
static you can also just inspect the various `html` files too.

### Pushing to production!

My approach to "publishing" this site is to render locally, push to github and
serve via github pages. In general this looks something like:

    $ python main.py
    $ git add <source-file.md>
    $ git add posts/<output-file.html>
    $ git commit
    # Write commit message
    $ git push

I choose not to render my static sites (the `python main.py` part) using a
continuous integration (CI) service, probably 50% laziness and 50% not wanting to add
a tiny layer of complexity that could break, **but** that's possible to do.

The [test_main.py](/{{root}}/test_main.py) file contains some unit tests and
I do use (CI) to make sure that doesn't break and also to make sure that `python
main.py` runs without failure.

### Why do this?

If you are happy with any of the **awesome** static site generators out there
you should not do this.

I've just often found myself wanting to make slight tweaks and either not being
willing to learn Ruby and not entirely satistfied with the tweaks that would
have been required for the Python options.

For example, [my personal "academic portfolio"](https://vknight.org/) (if that's
a thing?) site, uses a `yaml` database to render both the html and a latex/pdf
CV.
