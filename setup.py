# -*- coding: utf-8 -*-

"""Setup script for visual_genome."""

# Standard library imports
import os

# Third party imports
from setuptools import find_packages, setup

# Local imports
from visual_genome import __version__


HERE = os.path.abspath(os.path.dirname(__file__))


def get_description():
    """Get long description."""
    with open(os.path.join(HERE, 'README.rst'), 'r') as f:
        data = f.read()
    return data


REQUIREMENTS = ['requests']

setup(
    name='visual_genome',
    version=__version__,
    keywords=['Spyder', 'Plugin'],
    url='https://github.com/ranjaykrishna/visual_genome_python_driver',
    license='MIT',
    author='Ranjay Krishna',
    author_email='anjaykrishna@gmail.com',
    description='A pure python wrapper for the Visual Genome API',
    # long_description=get_description(),
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ])
