#!/usr/bin/env python3
import setuptools

# read the contents of your README file
#from os import path
#this_directory = path.abspath(path.dirname(__file__))
#with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()


setuptools.setup(
    name="pylbc",
    version="1.0",
    author="razaborg",
    author_email="contact@razaborg.fr",
    description="An (unofficial) python3 wrapper API around leboncoin.",
    long_description='',
    #long_description=long_description,
    #long_description_content_type='text/markdown',
    url="https://github.com/razaborg/pylbc",
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    python_requires='>=3',
    license='GNUPLv3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)

