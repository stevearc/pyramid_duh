""" Setup file """
import os
import sys

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()

REQUIREMENTS = [
    'pyramid',
    'six',
]

TEST_REQUIREMENTS = [
    'mock',
]

if sys.version_info[:2] < (2, 7):
    TEST_REQUIREMENTS.extend(['unittest2'])

if __name__ == "__main__":
    setup(
        name='pyramid_duh',
        version='0.1.2',
        description='Useful utilities for every pyramid app',
        long_description=README + '\n\n' + CHANGES,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Framework :: Pyramid',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Utilities',
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
