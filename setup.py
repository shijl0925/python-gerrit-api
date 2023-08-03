"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
# Always prefer setuptools over distutils
import ast
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()


def get_version() -> str:
    version = ""
    with open("gerrit/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = ast.literal_eval(line.split("=")[-1])
                break
    return version


setup(
    name="python-gerrit-api",
    # https://packaging.python.org/en/latest/single_source_version.html
    version=get_version(),
    description="Python wrapper for the Gerrit REST API.",
    long_description=long_description,
    url="https://github.com/shijl0925/python-gerrit-api",
    author="Jialiang Shi",
    author_email="kevin09254930sjl@gmail.com",
    license="MIT",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development",
    ],
    keywords="api gerrit client wrapper",
    packages=find_packages(exclude=["contrib", "docs", "test*"]),
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=required,
    extras_require={},
    package_data={},
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    data_files=[],
    # Test suite (required for Py2)
    test_suite="tests",
)
