import io
from setuptools import find_packages, setup


__author__ = 'Hassan Kibirige'
__email__ = 'has2k1@gmail.com'
__description__ = 'A gnuplot kernel for Jupyter'
__license__ = 'BSD'
__url__ = 'https://github.com/has2k1/gnuplot_kernel'
__classifiers__ = [
    'Framework :: IPython',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: System :: Shells',
]
__install_requires__ = [
    'metakernel >= 0.20.14',
    'notebook >= 5.5.0'
]
__packages__ = find_packages(
    include=['gnuplot_kernel', 'gnuplot_kernel.*']
)
__package_data__ = {'gnuplot_kernel': ['images/*.png']}

with io.open('gnuplot_kernel/kernel.py', encoding='utf-8') as fid:
    for line in fid:
        if line.startswith('__version__'):
            __version__ = line.strip().split()[-1][1:-1]
            break

with open('README.rst') as f:
    readme = f.read()

setup(name='gnuplot_kernel',
      author=__author__,
      maintainer=__author__,
      maintainer_email=__email__,
      version=__version__,
      description=__description__,
      long_description=readme,
      license=__license__,
      url=__url__,
      python_requires='>=3.6',
      install_requires=__install_requires__,
      packages=__packages__,
      package_data=__package_data__,
      classifiers=__classifiers__
      )
