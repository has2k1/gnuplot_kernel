from .kernel import GnuplotKernel
from .magics import register_ipython_magics

__all__ = ['GnuplotKernel']


def load_ipython_extension(ipython):
    """
    Load the extension in IPython
    """
    register_ipython_magics()
