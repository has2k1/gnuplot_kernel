import os
import weakref

from nose.tools import (assert_equal, assert_true, assert_false,
                        with_setup)
from metakernel.tests.utils import (get_kernel, get_log_text,
                                    clear_log_text)
from gnuplot_kernel import GnuplotKernel
from gnuplot_kernel.magics import GnuplotMagic

from .utils import remove_files

# Note: Empty lines after indented triple quoted may
# lead to empty statements which could obscure the
# final output.


# All kernels are registered to ensure a
# thorough cleanup
_get_kernel = get_kernel
KERNELS = weakref.WeakSet()


def get_kernel(klass=None):
    """
    Create & add to registry of live kernels
    """
    if klass:
        kernel = _get_kernel(klass)
    else:
        kernel = _get_kernel()
    KERNELS.add(kernel)
    return kernel


def teardown():
    """
    Shutdown all live kernels
    """
    while True:
        try:
            kernel = KERNELS.pop()
        except KeyError:
            break

        kernel.do_shutdown(restart=False)


# Normal workflow tests #

def test_inline_magic():
    kernel = get_kernel(GnuplotKernel)

    # gnuplot line magic changes the plot settings
    kernel.call_magic('%gnuplot pngcairo size 560, 420')
    assert_equal(kernel.plot_settings['backend'],
                 'pngcairo')
    assert_equal(kernel.plot_settings['format'],
                 'png')
    assert_equal(kernel.plot_settings['termspec'],
                 'pngcairo size 560, 420')


def test_print():
    kernel = get_kernel(GnuplotKernel)
    code = "print cos(0)"
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true('1.0' in text)


@with_setup(teardown=remove_files(('sine.png',
                                   'sine-cosine.png')))
def test_file_plots():
    kernel = get_kernel(GnuplotKernel)
    kernel.call_magic('%gnuplot pngcairo size 560, 420')

    # With a non-inline terminal plot gets created
    code = """
    set output 'sine.png'
    plot sin(x)
    """
    kernel.do_execute(code)
    assert_true(os.path.exists('sine.png'))
    clear_log_text(kernel)

    # Multiple line statement
    code = """
    set output 'sine-cosine.png'
    plot sin(x),\
         cos(x)
    """
    kernel.do_execute(code)
    assert_true(os.path.exists('sine-cosine.png'))


def test_inline_plots():
    kernel = get_kernel(GnuplotKernel)
    kernel.call_magic('%gnuplot inline')

    # inline plot creates data
    code = """
    plot sin(x)
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true('Display Data' in text)
    clear_log_text(kernel)

    # multiple plot statements data
    code = """
    plot sin(x)
    plot cos(x)
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true(text.count('Display Data') == 2)
    clear_log_text(kernel)

    # svg
    kernel.call_magic('%gnuplot inline svg')
    code = """
    plot tan(x)
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true('Display Data' in text)
    clear_log_text(kernel)


def test_plot_abbreviations():
    kernel = get_kernel(GnuplotKernel)

    # Short names for the plot statements can be used
    # to create inline plots
    code = """
    plot sin(x)
    p cos(x)
    rep
    unset key
    sp x**2+y**2, x**2-y**2
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true(text.count('Display Data') == 4)


def test_multiplot():
    kernel = get_kernel(GnuplotKernel)

    # multiplot
    code = """
    set multiplot layout 2,1
    plot sin(x)
    plot cos(x)
    unset multiplot
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true(text.count('Display Data') == 1)


def test_help():
    kernel = get_kernel(GnuplotKernel)

    # The help commands should not get
    # stuck in pagers.

    # Fancy notebook help
    code = 'terminal?'
    kernel.do_execute(code)
    text = get_log_text(kernel).lower()
    assert_true('subtopic' in text)
    clear_log_text(kernel)

    # help by gnuplot statement
    code = 'help print'
    kernel.do_execute(code)
    text = get_log_text(kernel).lower()
    assert_true('syntax' in text)
    clear_log_text(kernel)


def test_badinput():
    kernel = get_kernel(GnuplotKernel)

    # No code that endswith a backslash
    code = 'plot sin(x),\\'
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true('backslash' in text)


def test_gnuplot_error_message():
    kernel = get_kernel(GnuplotKernel)

    # The error messages gets to the kernel
    code = 'plot [1,2][] sin(x)'
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true(' ^' in text)


def test_bad_prompt():
    kernel = get_kernel(GnuplotKernel)
    # Anything other than 'gnuplot> '
    # is a bad prompt
    code = 'set multiplot'
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert_true('warning' in text.lower())


# magics #

@with_setup(teardown=remove_files('cosine.png'))
def test_cell_magic():
    # To simulate '%load_ext gnuplot_kernel';
    # create a main kernel, a gnuplot kernel and
    # a gnuplot magic that uses the gnuplot kernel.
    # Then manually register the gnuplot magic into
    # the main kernel.
    kernel = get_kernel()
    gkernel = GnuplotKernel()
    gmagic = GnuplotMagic(gkernel)
    gkernel.makeSubkernel(kernel)
    kernel.line_magics['gnuplot'] = gmagic
    kernel.cell_magics['gnuplot'] = gmagic

    # inline output
    code = """%%gnuplot
    plot cos(x)
    """
    kernel.do_execute(code)
    assert_true('Display Data' in get_log_text(kernel))
    clear_log_text(kernel)

    # file output
    kernel.call_magic('%gnuplot pngcairo size 560,420')
    code = """%%gnuplot
    set output 'cosine.png'
    plot cos(x)
    """
    kernel.do_execute(code)
    assert_true(os.path.exists('cosine.png'))
    clear_log_text(kernel)


@with_setup(teardown=remove_files('sine+cosine.png'))
def test_reset_cell_magic():
    kernel = get_kernel(GnuplotKernel)

    # Use reset statements that have testable effect
    code = """%%reset
    set output 'sine+cosine.png'
    plot sin(x) + cos(x)
    """
    kernel.call_magic(code)
    assert_false(os.path.exists('sine+cosine.png'))

    code = """
    unset key
    """
    kernel.do_execute(code)
    assert_true(os.path.exists('sine+cosine.png'))


def test_reset_line_magic():
    kernel = get_kernel(GnuplotKernel)

    # Create a reset
    code = """%%reset
    set output 'sine+sine.png'
    plot sin(x) + sin(x)
    """
    kernel.call_magic(code)

    # Remove the reset, execute some code and
    # make sure there are no effects
    kernel.call_magic('%reset')
    code = """
    unset key
    """
    kernel.do_execute(code)
    assert_false(os.path.exists('sine+sine.png'))

    # Bad inline backend
    # metakernel messes this exception!!
    # with assert_raises(ValueError):
    #     kernel.call_magic('%gnuplot inline qt')


# utils tests #

def test_remove_files():
    filename = './antigravity.txt'
    func = remove_files(filename)

    # Create file
    # Verify it exists
    # Remove it
    # Verify it does not exist
    # Remove it again, nothing happens

    with open(filename, 'w'):
        pass

    assert_true(os.path.exists(filename))
    func()

    assert_false(os.path.exists(filename))
    func()
