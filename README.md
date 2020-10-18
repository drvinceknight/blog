# Personal blog site.

Source code for a blog written by [Vince Knight](@drvinceknight). Topics
covered:

- Python
- Mathematics and stochastic things
- Usually both of the above

## Render

The course code of this blog is markdown files. A conda environment with all
required code is include.

To create the environment:

```
$ python -m venv blg-env
```

To source the environment:

```
$ source blog-env/bin/activate
```

To install the Python and R dependencies.

```
$ python -m invoke setup
```

To render the html:

```
$ inv build
```
