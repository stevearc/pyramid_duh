""" Setup file """
import os
import sys

from setuptools import setup, find_packages
from pyramid_duh_version import git_version, UpdateVersion


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()

REQUIREMENTS = [
    'pyramid',
]

TEST_REQUIREMENTS = [
    'mock',
]

if sys.version_info[:2] < (2, 7):
    REQUIREMENTS.extend(['unittest2'])

if __name__ == "__main__":
    setup(
        name='pyramid_duh',
        version=git_version('pyramid_duh'),
        cmdclass={'update_version': UpdateVersion},
        description='Useful utilities for every pyramid app',
        long_description=README + '\n\n' + CHANGES,
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
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
        url='http://pyramid-duh.readthedocs.org/',
        keywords='pyramid util utility',
        license='MIT',
        zip_safe=False,
        include_package_data=True,
        packages=find_packages(exclude=('tests',)),
        install_requires=REQUIREMENTS,
        tests_require=REQUIREMENTS + TEST_REQUIREMENTS,
        test_suite='tests',
    )
