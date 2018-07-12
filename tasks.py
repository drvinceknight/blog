from invoke import task

@task
def test(c):
    """
    Run test suite
    """
    c.run("python -m pytest")

@task
def build(c):
    """
    Run test suite
    """
    c.run("python main.py")
