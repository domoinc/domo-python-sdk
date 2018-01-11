from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
description = 'The official Python3 Domo API SDK - Domo, Inc.'

# Try to get the long description from the README file
try:
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError as fnfe:
    long_description=description

setup(
    name='pydomo',
    version='0.2.2.1',
    description=description,
    long_description=long_description,
    author='Bobby Swingler',
    author_email='bobby.swingler@domo.com',
    url='https://github.com/domoinc/domo-python-sdk',
    download_url='https://github.com/domoinc/domo-python-sdk/tarball/0.2.2.1',
    keywords='domo api sdk',
    license='MIT',
    packages=find_packages(exclude=['examples']),
    install_requires=[
        'requests',
        'requests_toolbelt',
    ],
    python_requires='>=3',
)
