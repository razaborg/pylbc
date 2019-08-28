#!/usr/bin/env python3
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylbc-razaborg",
    version="1.0",
    author="razaborg",
    author_email="contact@razaborg.fr",
    description="An (unofficial) python3 wrapper API around leboncoin.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/razaborg/pylbc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)

