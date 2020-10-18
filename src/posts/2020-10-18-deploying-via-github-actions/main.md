title: Deploying a static site (built with R and Python) via github actions
description: A post showing how to deploy a static site using github actions.
---

This blog is a static site with source files written in markdown, Jupyter or R
markdown. Up until this post I have always generated the html locally and push
that to github which in turn serves the pages using Github pages:
https://pages.github.com

In this blog post I will describe how to use Github Actions
https://github.com/features/actions to not only build the static files but also
deploy them.

The repo for this blog is available here: https://github.com/drvinceknight/blog
and this is what the structure looks like:

```bash
LICENSE
README.md
_build/
assets/
blog-env/
requirements.txt
setup.R
src
|--- posts/
    |--- 2018-07-10-just-enough-static-site-generator
    |--- 2018-07-11-examining-the-relationship-between-student-performance-and-video-interactions
    |--- 2018-11-23-zipping-iterators
    |--- 2018-11-26-galton-board
    |--- 2018-12-19-continuous-time-markov-chains
    |--- 2019-04-03-testing-zd
    |--- 2019-05-06-making-kernel-available-to-jupyter
    |--- 2019-05-24-reproducing-axelrods-first-tournament
    |--- 2020-02-26-computing-nash-equilibria-in-R
    |--- 2020-10-18-deploying-via-github-actions
tasks.py
.github/workflows/
```

To use github actions we need to put a configuration file in the
`.github/workflows/` directory.

In this file we include the specific instructions to build and deploy the site
when the `main` branch is altered (this is my default branch) and push to the
`gh-pages`
branch which I have set to be served via github actions:

<img src="/{{root}}/src/posts/2020-10-18-deploying-via-github-actions/img/screenshot/main.png" class="img-fluid" alt="Responsive image">

This setting is accessible via the specific repository's settings page.

```yml
name: deploy

# Only run this when the main branch changes
on:
  push:
    branches:
    - main
    paths:
    - src/**

# This job installs dependencies, build the site, and pushes it to `gh-pages``
jobs:
  deploy-book:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    # Install python
    - name: Set up Python 3.8
      uses: actions/setup-python@v1
      with:
        python-version: 3.8
    # Install R
    - name: Set up R 4.0.3
      uses: r-lib/actions/setup-r@v1
      with:
        r-version: '4.0.3'

    - name: Install python and R dependencies
      run: |
        python -m invoke setup

    # Build the site
    - name: Build the site
      run: |
        python -m invoke build

    # Push the book's HTML to github-pages
    - name: GitHub Pages action
      uses: peaceiris/actions-gh-pages@v3.6.1
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./_build/
```

There are two bespoke tasks:

- Install python and R dependencies: `python -m invoke setup`
- Build the site: `python -m invoke build`

These make use of the python library `invoke` <http://www.pyinvoke.org> which is
similar to `make` and allows me to abstract the specific tasks related to those
two steps.  You can see these in the `tasks.py` file.
