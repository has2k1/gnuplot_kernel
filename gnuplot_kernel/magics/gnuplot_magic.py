from __future__ import print_function

from IPython.core.magic import (register_line_magic,
                                register_cell_magic)
from metakernel import Magic


class GnuplotMagic(Magic):
    def __init__(self, kernel):
        """
        GnuplotMagic

        Parameters
        ----------
        kernel : GnuplotKernel
            Kernel used to execute the magic code
        """
        super(GnuplotMagic, self).__init__(kernel)

    def eval(self, code):
        """
        Evaluate code useing the gnuplot kernel
        """
        return self.kernel.do_execute_direct(code)

    def print(self, text):
        """
        Print text if it is not empty
        """
        if text and text.output.strip():
            self.kernel.Display(text)

    def line_gnuplot(self, *args):
        """
        %gnuplot CODE - evaluate code as gnuplot

        This line magic will evaluate the CODE to setup or
        unset inline plots. This magic should be used instead
        of the plot magic

        Examples:
            %gnuplot inline pngcairo enhanced transparent size 560,420
            %gnuplot inline svg enhanced size 560,420 fixed
            %gnuplot inline jpeg enhanced nointerlace
            %gnuplot qt

        """
        backend, terminal, termspec = _parse_args(args)
        terminal = terminal or 'pngcairo'
        inline_terminals = {'pngcairo': 'png',
                            'png': 'png',
                            'jpeg': 'jpg',
                            'svg': 'svg'}
        format = inline_terminals.get(terminal, 'png')

        if backend == 'inline':
            if terminal not in inline_terminals:
                msg = ("For inline plots, the terminal must be "
                       "one of pngcairo, jpeg, svg or png")
                raise ValueError(msg)

        self.kernel.plot_settings['backend'] = backend
        self.kernel.plot_settings['termspec'] = termspec
        self.kernel.plot_settings['format'] = format
        self.kernel.handle_plot_settings()

    def cell_gnuplot(self):
        """
        %%gnuplot - Run gnuplot commands

        Example:
            %%gnuplot
            unset border
            unset xtics
            g(x) = cos(2*x)/sin(x)

        Note: this is a persistent connection to a gnuplot shell.
        The working directory is synchronized to that of the notebook
        before and after each call.
        """
        result = self.eval(self.code)
        self.print(result)


def register_magics(kernel):
    """
    Make the gnuplot magic available for the GnuplotKernel
    """
    kernel.register_magics(GnuplotMagic)


def register_ipython_magics():
    """
    Register magics for the running kernel

    The magics themselve use a special kernel that
    understands gnuplot.
    """
    from ..kernel import GnuplotKernel

    # Kernel to run the both the line magic (%gnuplot)
    # and cell magic (%%gnuplot) statements
    # See: GnuplotKernel for a full notebook kernel
    kernel = GnuplotKernel()
    magic = GnuplotMagic(kernel)

    # This kernel that is used by the magics is
    # not the main kernel and it may not have access
    # to some functionality. This connects it to the
    # main kernel.
    from IPython import get_ipython
    ip = get_ipython()
    kernel.makeSubkernel(ip.parent)

    # Make magics callable:
    kernel.line_magics['gnuplot'] = magic
    kernel.cell_magics['gnuplot'] = magic

    @register_line_magic
    def gnuplot(line):
        magic.line_gnuplot(line)

    del gnuplot

    @register_cell_magic
    def gnuplot(line, cell):
        magic.code = cell
        magic.cell_gnuplot()


def _parse_args(args):
    """
    Process the gnuplot line magic arguments
    """
    if len(args) > 1:
        raise TypeError()

    sargs = args[0].split()
    backend = sargs[0]
    if backend == 'inline':
        try:
            termspec = ' '.join(sargs[1:])
            terminal = sargs[1]
        except IndexError:
            termspec = None
            terminal = None
    else:
        termspec = args[0]
        terminal = sargs[0]

    return backend, terminal, termspec
