import sys
import io
import os
import json
import pkgutil

from distutils import log
from distutils.command.install import install
from setuptools import find_packages, setup


with io.open('gnuplot_kernel/kernel.py', encoding='utf-8') as fid:
    for line in fid:
        if line.startswith('__version__'):
            __version__ = line.strip().split()[-1][1:-1]
            break

with open('README.rst') as f:
    readme = f.read()

setup(name='gnuplot_kernel',
      version=__version__,
      description='A gnuplot kernel for Jupyter',
      long_description=readme,
      author='Hassan Kibirige',
      author_email='has2k1@gmail.com',
      license='BSD',
      url="https://github.com/has2k1/gnuplot_kernel",
      install_requires=[
          'metakernel >= 0.20.14',
          'notebook >= 5.4.0'],
      packages=find_packages(
          include=['gnuplot_kernel', 'gnuplot_kernel.*']
      ),
      package_data={'gnuplot_kernel': ['images/*.png']},
      classifiers=[
          'Framework :: IPython',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: System :: Shells',
      ]
      )
