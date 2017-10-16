from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pydomo',
    version='0.2.1',
    description='The official Python3 Domo API SDK - Domo, Inc.',
    long_description=long_description,
    author='Bobby Swingler',
    author_email='bobby.swingler@domo.com',
    url='https://github.com/domoinc/domo-python-sdk',
    keywords='domo api sdk',
    license='MIT',
    packages=find_packages(exclude=['examples']),
    install_requires=[
        'requests',
        'requests_toolbelt',
    ],
    python_requires='>=3',
)
