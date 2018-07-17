from invoke import task

@task
def test(c):
    c.run("pytest --doctest-glob='*.md'")

@task
def main(c):
    c.run("python main.py")
