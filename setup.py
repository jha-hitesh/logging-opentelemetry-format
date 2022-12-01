"""Library Metadata Information."""

from setuptools import find_packages
from setuptools import setup

description = ("opentelemetry formatter for python logging module.")

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="logging_opentelemetry_format",
    version="0.0.1",
    author="hitesh jha",
    author_email="hitesh4official@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jha-hitesh/logging-opentelemetry-format",
    packages=find_packages(
        exclude=(
            "tests"
        )
    ),
    license="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "ujson",
        "opentelemetry-api==1.14.0",
        "opentelemetry-sdk==1.14.0"
    ],
    python_requires=">=3.6",
)
