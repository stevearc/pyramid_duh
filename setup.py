""" Setup file """
import os
import sys

from setuptools import setup, find_packages
from version_helper import git_version


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()

REQUIREMENTS = [
    'pyramid',
]

if sys.version_info[:2] < (2, 7):
    REQUIREMENTS.extend(['unittest2'])

if __name__ == "__main__":
    setup(
        name='pyramid_duh',
        description='Useful utilities for every pyramid app',
        long_description=README + '\n\n' + CHANGES,
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Development Status :: 4 - Beta',
            'Framework :: Pylons',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Topic :: Internet :: WWW/HTTP',
        ],
        author='Steven Arcangeli',
        author_email='arcangeli07@gmail.com',
        url='http://github.com/stevearc/pyramid_duh',
        keywords='pyramid util utility',
        license='MIT',
        zip_safe=False,
        include_package_data=True,
        packages=find_packages(),
        install_requires=REQUIREMENTS,
        tests_require=REQUIREMENTS,
        **git_version()
    )
