#!/usr/bin/env python
import os

from setuptools import setup, find_packages


if __name__ == "__main__":

    base_dir = os.path.dirname(__file__)

    about = {}
    with open(os.path.join(base_dir, "mtl", "__about__.py")) as f:
        exec(f.read(), about)

    install_requirements = [
        'beautifulsoup4>=4.5.1',
        'click>=6.6',
        'Flask>=0.11.1',
        'Flask-Compress>=1.4.0',
        'google-api-python-client>=1.5.5',
        'httplib2>=0.9.2',
        'itsdangerous>=0.24',
        'Jinja2>=2.8',
        'MarkupSafe>=0.23',
        'oauth2client>=4.0.0',
        'pyasn1>=0.1.9',
        'pyasn1-modules>=0.0.8',
        'PyDrive>=1.3.1',
        'PyYAML>=3.12',
        'requests>=2.11.1',
        'rsa>=3.4.2',
        'six>=1.10.0',
        'uritemplate>=3.0.0',
        'waitress>=1.0.1',
        'Werkzeug>=0.11.11',
    ]

    setup(
        name=about['__title__'],
        version=about['__version__'],

        description=about['__summary__'],
        url=about["__uri__"],

        author=about["__author__"],

        package_dir={'': 'src'},
        packages=find_packages(where='src'),
        include_package_data=True,

        install_requires=install_requirements,

        zip_safe=False,

        entry_points='''
            [console_scripts]
        '''
    )