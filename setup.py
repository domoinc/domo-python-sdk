from distutils.core import setup


setup(
    name='pydomo',
    version='0.1.2',
    description='The official python3 Domo API SDK - Domo, Inc.',
    author='Bobby Swingler',
    author_email='bobby.swingler@domo.com',
    url='https://github.com/domoinc/domo-python-sdk',
    keywords=['domo', 'api', 'sdk'],
    license='MIT',
    packages=['pydomo',
              'pydomo.datasets',
              'pydomo.groups',
              'pydomo.streams',
              'pydomo.users'],
    requires=[
        'requests',
        'jsonpickle'
    ]
)
