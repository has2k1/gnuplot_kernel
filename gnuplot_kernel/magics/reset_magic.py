from __future__ import print_function

from metakernel import Magic


class ResetMagic(Magic):

    def line_reset(self, *line):
        """
        %reset - Clear any reset

        Example:
            %reset
        """
        self.kernel.reset_code = ''

    def cell_reset(self, line):
        """
        %%reset - Change the gnuplot terminal

        This cell magic is used to specify statements that will
        silently run after every cell execution.

        Example:
            %%reset
            set key
        """
        self.kernel.reset_code = self.code


def register_magics(kernel):
    """
    Make the reset magic available for the GnuplotKernel
    """
    kernel.register_magics(ResetMagic)
