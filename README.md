# A Jupyter/IPython kernel for Gnuplot


[![Release](https://img.shields.io/pypi/v/gnuplot_kernel.svg)](https://pypi.python.org/pypi/gnuplot_kernel)
[![License](https://img.shields.io/pypi/l/gnuplot_kernel.svg)](https://pypi.python.org/pypi/gnuplot_kernel)
[![Build Status](https://github.com/has2k1/plotnine/workflows/build/badge.svg?branch=main)](https://github.com/has2k1/plotnine/actions?query=branch%3Amain+workflow%3A%22build%22)
[![Coverage](https://coveralls.io/repos/github/has2k1/gnuplot_kernel/badge.svg?branch=main)](https://coveralls.io/github/has2k1/gnuplot_kernel?branch=main)

`gnuplot_kernel` has been developed for use specifically with `Jupyter Notebook`.
It can also be loaded as an `IPython` extension allowing for `gnuplot` code in the same `notebook`
as `python` code.

## Installation

Official release

```console
$ pip install gnuplot_kernel
$ python -m gnuplot_kernel install --user
```


The last command installs a kernel spec file for the current python installation. This
is the file that allows you to choose a jupyter kernel in a notebook.

Development version

```console
$ pip install git+https://github.com/has2k1/gnuplot_kernel.git@master
$ python -m gnuplot_kernel install --user
```

## Requires

- System installation of [Gnuplot](http://www.gnuplot.info/)

## Documentation

1. [Example Notebooks](https://github.com/has2k1/gnuplot_kernel/tree/main/examples) for `gnuplot_kernel`.
2. [Metakernel magics](https://github.com/Calysto/metakernel/blob/master/metakernel/magics/README.md), these are available when using `gnuplot_kernel`.
