from .kernel import GnuplotKernel
from .magics import register_ipython_magics

__all__ = ['GnuplotKernel']

from importlib.metadata import version, PackageNotFoundError


try:
    __version__ = version('gnuplot_kernel')
except PackageNotFoundError:
    # package is not installed
    pass


def load_ipython_extension(ipython):
    """
    Load the extension in IPython
    """
    register_ipython_magics()
