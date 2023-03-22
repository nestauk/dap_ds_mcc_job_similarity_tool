"""mcc_sussex"""
from pathlib import Path
from setuptools import find_packages
from setuptools import setup


def read_lines(path):
    """Read lines of `path`."""
    with open(path) as f:
        return f.read().splitlines()


BASE_DIR = Path(__file__).parent


setup(
    name="mcc_sussex",
    long_description=open(BASE_DIR / "README.md").read(),
    install_requires=read_lines(BASE_DIR / "requirements.txt"),
    packages=find_packages(exclude=["docs"]),
    version="0.1.0",
    description="Building an app to recommend similar jobs based on skills",
    author="Nesta",
    license="MIT",
)