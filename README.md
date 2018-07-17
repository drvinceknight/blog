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
$ conda env create -f environment.yml
```

To source the environment:

```
$ conda activate blog
```

To render the html:

```
$ inv main
```

To test all the (python) code written:

```
$ inv test
```
