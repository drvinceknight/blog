title: Making a kernel available to Jupyter
description: A short post with the command needed to make a given kernel appear in Jupyter dropdown menu
---

This blog post is in the category of "write it down somewhere so I don't forget
it" but it might be helpful to others.

When I start my computer I run a Jupyter kernel from my home directory:

```
$ jupyter notebook
```

I am also a big fan of conda environments, essentially having an environment for
any given research project.

It is possible to make each and everyone of these environments available to
Jupyter so that when you click on the `new` button you can decide which
environment to use:

![](/{{root}}/src/2019-05-06-making-kernel-available-to-jupyter/img/dropdown_menu.png)

Having installed Jupyter in the `folk_theorem` environment, here is how you make
that in the dropdown menu:

```
python -m ipykernel install --user --name folk_theorem --display-name "Folk Theorem"
```
