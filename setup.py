from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
description = 'The official Python3 Domo API SDK - Domo, Inc.'
long_description = 'See https://github.com/domoinc/domo-python-sdk for more details.'

setup(
    name='pydomo',
    version='0.3.0.14',
    description=description,
    long_description=long_description,
    author='Jeremy Morris',
    author_email='jeremy.morris@domo.com',
    url='https://github.com/domoinc/domo-python-sdk',
    download_url='https://github.com/domoinc/domo-python-sdk/tarball/0.2.2.1',
    keywords='domo api sdk',
    license='MIT',
    packages=find_packages(exclude=['examples']),
    install_requires=[
        'pandas',
        'requests',
        'requests_toolbelt',
    ],
    python_requires='>=3',
)
