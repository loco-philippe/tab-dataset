# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 2023

@author: philippe@loco-labs.io
"""

import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="tab_dataset",
    version="0.1.0",
    description="TAB-dataset : A tool for structuring tabular data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loco-philippe/tab_dataset/blob/main/README.md",
    author="Philippe Thomy",
    author_email="philippe@loco-labs.io",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"],
    keywords="tabular data, open data, environmental data",
    packages=find_packages(include=['tab_dataset', 'tab_dataset.*']),
    python_requires=">=3.9, <4",
    install_requires=[]
)
