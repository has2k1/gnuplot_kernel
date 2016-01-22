####################################
A Jupyter/IPython kernel for gnuplot
####################################

`gnuplot_kernel` has been developed for use specifically with
`Jupyter Notebook`. It can also be loaded as an `IPython`
extension allowing for `gnuplot` code in the same `notebook`
as `python` code.


Installation
============

**Official version**

.. code-block:: bash

   pip install gnuplot_kernel

   # or to upgrade
   pip install --upgrade gnuplot_kernel

**Development version**

.. code-block:: bash

   pip install git+https://github.com/has2k1/gnuplot_kernel.git@master


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
