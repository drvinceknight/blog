title: Setting up a spell checker for LaTeX (or anything really) via github actions
description: A post showing how to use aspell and github actions to check spelling.
---

This post will describe using `aspell` <http://aspell.net> (a free and open
source spell checker), a bit of python glue and github actions to setup
spell checking for LaTeX documents (although this can be used to spell check
other document types as well). We will also add a check that confirms the LaTeX
syntax compiles.

Let us start with a directory with the following structure:

```bash
README.md
|--- tex/
    |--- README.md
    |--- main.tex
```

We will use that `tex` directory to keep all our LaTeX apart from the rest of
the repository (and specifically some of the glue we need to get github actions
to work).

The `README.md` files are not necessary for this but a good thing to have
to document the contents of a directory.

## Using `aspell`

We are going to use `aspell` as the spell checker. Installation instructions are
available at <http://aspell.net>. It is both `brew` (macOS) and `apt` (ubuntu)
installable:

```bash
$ brew instal aspell
```

If we want to run the spellchecker on the LaTeX documents we run:

```bash
$ aspell -t list < tex/*.tex
```

- The `-t` ensures aspell filters out various LaTeX commands.
- `list` ensures that all misspelt words are just listed to screen.
- `tex/**.tex` will go through all subdirectories of `tex` and find the `.tex`
  files.

**Whether or not there are misspelt words the exit code for that command will
always be 0.**

You can confirm this by running:

```bash
$ echo $?
```

A good tutorial/explanation of exit codes is
<https://shapeshed.com/unix-exit-codes/> but when we start using github actions
a 0 exit code will be displayed with a big green tick and everything will be
assumed fine. What we want is for a non zero exit code to be returned when there
is any misspelt word. We will use some python glue for this.

## Some Python glue

First of all we will create a python file `known.py` in the root of our
directory with a `set` of extra known words (I'm pretty sure the dictionary
`aspell` uses does not know about `TikTok` for example).


```python
words = {"TikTok"}
```

`aspell` does directly have functionality to add a custom list of words but this
approach has proven to have further benefits in my use cases (I won't go over
those now).

We will now use the Python library `invoke` <http://www.pyinvoke.org> which can
be used to create a set of tasks to be run.

First we add `invoke` to a `requirements.txt` file to make a note of it as a
dependency:

```
invoke>=1.4.1
```

There I am choosing to specify the lower bound of the version to use but you
could be more or indeed less specific if you wanted.

We now write a `tasks.py` file which will include all the instructions to run
`aspell` on the `tex` files but also return a non zero exit code if a word is
not spelt correctly.

```python
import subprocess
import pathlib
import sys

from invoke import task

import known

def get_files_to_check():
    """
    A generator that returns paths of latex files.

    Note that this could be extended to yield other files as necessary.
    """
    for path in pathlib.Path("tex/").glob("*.tex"):
        yield path


@task
def spellcheck(c):
    """
    Run the book through a spell checker.

    Known exceptions are in `known.py`
    """
    exit_code = 0

    for tex_path in get_files_to_check():

        tex = tex_path.read_text()
        aspell_output = subprocess.check_output(
            ["aspell", "-t", "--list", "--lang=en_GB"], input=tex, text=True
        )
        incorrect_words = set(aspell_output.split("\n")) - {""} - known.words
        if len(incorrect_words) > 0:
            print(f"In {tex_path} the following words are not known: ")
            for string in sorted(incorrect_words):
                print(string)
            exit_code = 1

    sys.exit(exit_code)
```

We can now run:

```bash
$ inv spellcheck
```

And this will not only return a list of misspelt words but also have the correct
exit code as necessary.

## The full directory

The final directory will look like:

```bash
README.md
|--- tex/
    |--- README.md
    |--- main.tex
|... .github/
    |--- workflows/
        |--- prose.yml
know.py
tasks.py
requirements.txt
```

## The github actions configuration file

The final step is to write a configuration file with instructions for the
commands to be run by Github Actions whenever we want it to check what we have
committed.

In `.github/workflows` we put a `prose.yml` file:

```
name: Test prose

on:
  push:
  pull_request:

jobs:
  build:

    runs-on: ${{ matrix.os }}
    strategy:
      max-parallel: 4
      matrix:
        os: [ubuntu-latest]
        python-version: [3.8]

    steps:
    - uses: actions/checkout@v1
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install python dependencies
      run: |
        python -m pip install -U pip
        python -m pip install -r requirements.txt

    - name: Install aspell (spell checker)
      run: |
        sudo apt-get install aspell aspell-en

    - name: Run spell checker
      run: |
        inv spellcheck

    - name: Install LaTeX
      run: |
        sudo apt-get update
        sudo apt-get install -y texlive-latex-extra
        sudo apt-get install -y texlive-xetex
        sudo apt-get install latexmk
        sudo apt-get install texlive-science

    - name: Check that document compiles
      run: |
        pdflatex tex/main.tex
```

Note that we could call this file whatever we want but I suggest `prose.yml` to
indicate that it's a check on the writing. We could add other files with checks
for code or other things.

The configuration file starts by giving instructions on the operating system we
want to use. I suggest `ubuntu-latest` as opposed to a `macOS` or `windows`
alternative as it is straightforward to install everything we need on `ubuntu`.

Every subsequent block in that file has a `name: ` that indicates what is
happening:

- `Install python dependencies`: this install the python dependencies
  specifically anything in the `requirements.txt` file.
- `Install aspell`: this installs the spellchecker using the ubuntu repository.
- `Run spell checker`: this using the `invoke` task we wrote earlier to run the
  spell checker.

The final two tasks are not ones we discussed earlier:

- `Install LaTeX`: this install LaTeX and a number of useful LaTeX libraries for
  mathematical/scientific writing.
- `Check that document compiles`: this compiles the document. LaTeX here will
  not return an exit code of 0 if the document fails to compile.

## Summary

This setup lets you use a github based workflow for checking and review of
writing.

It can be further enhanced with other text checkers such as `alex`
<https://github.com/get-alex/alex> or `proselint` <http://proselint.com>.

An example of this is my current programming course text which uses a number of
different elements of continuous integration to help me avoid errors:
<https://vknight.org/pfm/about-this-book/how-is-this-book-written/main.html>.
