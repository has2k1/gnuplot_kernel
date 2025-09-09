"""
Gnuplot Kernel Package
"""

from contextlib import suppress
from importlib.metadata import PackageNotFoundError

from .kernel import GnuplotKernel
from .magics import register_ipython_magics
from .utils import get_version

__all__ = ["GnuplotKernel"]


with suppress(PackageNotFoundError):
    __version__ = get_version("gnuplot_kernel")


def load_ipython_extension(ipython):
    """
    Load the extension in IPython
    """
    register_ipython_magics()
