####################################
A Jupyter/IPython kernel for Gnuplot
####################################

=================    ===============
Latest Release       |release|_
License              |license|_
Build Status         |buildstatus|_
Coverage             |coverage|_
=================    ===============


`gnuplot_kernel` has been developed for use specifically with
`Jupyter Notebook`. It can also be loaded as an `IPython`
extension allowing for `gnuplot` code in the same `notebook`
as `python` code.


Installation
============

**Official version**

.. code-block:: bash

   pip install gnuplot_kernel
   python -m gnuplot_kernel install --user

The last command installs a kernel spec file for the current python installation. This
is the file that allows you to choose a jupyter kernel in a notebook.

**Development version**

.. code-block:: bash

   pip install git+https://github.com/has2k1/gnuplot_kernel.git@master
   python -m gnuplot_kernel install --user


Requires
========

- System installation of `Gnuplot`_
- `Notebook`_ (IPython/Jupyter Notebook)
- `Metakernel`_


Documentation
=============

1. `Example Notebooks`_ for `gnuplot_kernel`.
2. `Metakernel magics`_, these are available when using `gnuplot_kernel`.


.. _`Notebook`: https://github.com/jupyter/notebook
.. _`Gnuplot`: http://www.gnuplot.info/
.. _`Example Notebooks`: https://github.com/has2k1/gnuplot_kernel/tree/master/examples
.. _`Metakernel`: https://github.com/Calysto/metakernel
.. _`Metakernel magics`: https://github.com/Calysto/metakernel/blob/master/metakernel/magics/README.md

.. |release| image:: https://img.shields.io/pypi/v/gnuplot_kernel.svg
.. _release: https://pypi.python.org/pypi/gnuplot_kernel

.. |license| image:: https://img.shields.io/pypi/l/gnuplot_kernel.svg
.. _license: https://pypi.python.org/pypi/gnuplot_kernel

.. |buildstatus| image:: https://api.travis-ci.org/has2k1/gnuplot_kernel.svg?branch=master
.. _buildstatus: https://travis-ci.org/has2k1/gnuplot_kernel

.. |coverage| image:: https://coveralls.io/repos/github/has2k1/gnuplot_kernel/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/has2k1/gnuplot_kernel?branch=master
