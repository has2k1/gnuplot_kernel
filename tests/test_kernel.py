import weakref
from pathlib import Path

from metakernel.tests.utils import clear_log_text, get_kernel, get_log_text

from gnuplot_kernel import GnuplotKernel
from gnuplot_kernel.magics import GnuplotMagic

from .conftest import remove_files

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
    kernel.call_magic("%gnuplot pngcairo size 560, 420")
    assert kernel.plot_settings["backend"] == "pngcairo"
    assert kernel.plot_settings["format"] == "png"
    assert kernel.plot_settings["termspec"] == "pngcairo size 560, 420"


def test_print():
    kernel = get_kernel(GnuplotKernel)
    code = "print cos(0)"
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert "1.0" in text


def test_file_plots():
    kernel = get_kernel(GnuplotKernel)
    kernel.call_magic("%gnuplot pngcairo size 560, 420")

    # With a non-inline terminal plot gets created
    code = """
    set output 'sine.png'
    plot sin(x)
    """
    kernel.do_execute(code)
    assert Path("sine.png").exists()
    clear_log_text(kernel)

    # Multiple line statement
    code = """
    set output 'sine-cosine.png'
    plot sin(x),\
         cos(x)
    """
    kernel.do_execute(code)
    assert Path("sine-cosine.png").exists()

    # Multiple line statement
    code = """
    set output 'tan.png'
    plot tan(x)
    set output 'tan2.png'
    replot
    """
    kernel.do_execute(code)
    assert Path("tan.png").exists()
    assert Path("tan2.png").exists()

    remove_files("sine.png", "sine-cosine.png")
    remove_files("tan.png", "tan2.png")


def test_inline_plots():
    kernel = get_kernel(GnuplotKernel)
    kernel.call_magic("%gnuplot inline")

    # inline plot creates data
    code = """
    plot sin(x)
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert "Display Data" in text
    clear_log_text(kernel)

    # multiple plot statements data
    code = """
    plot sin(x)
    plot cos(x)
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert text.count("Display Data") == 2
    clear_log_text(kernel)

    # svg
    kernel.call_magic("%gnuplot inline svg")
    code = """
    plot tan(x)
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert "Display Data" in text
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
    assert text.count("Display Data") == 4


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
    assert text.count("Display Data") == 1

    # With output
    code = """
    set terminal pncairo
    set output 'multiplot-sin-cos.png'
    set multiplot layout 2, 1
    plot sin(x)
    plot cos(x)
    unset multiplot
    unset output
    """
    kernel.do_execute(code)
    assert Path("multiplot-sin-cos.png").exists()
    remove_files("multiplot-sin-cos.png")


def test_help():
    kernel = get_kernel(GnuplotKernel)

    # The help commands should not get
    # stuck in pagers.

    # Fancy notebook help
    code = "terminal?"
    kernel.do_execute(code)
    text = get_log_text(kernel).lower()
    assert "subtopic" in text
    clear_log_text(kernel)

    # help by gnuplot statement
    code = "help print"
    kernel.do_execute(code)
    text = get_log_text(kernel).lower()
    assert "syntax" in text
    clear_log_text(kernel)


def test_badinput():
    kernel = get_kernel(GnuplotKernel)

    # No code that endswith a backslash
    code = "plot sin(x),\\"
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert "backslash" in text


def test_gnuplot_error_message():
    kernel = get_kernel(GnuplotKernel)

    # The error messages gets to the kernel
    code = "plot [1,2][] sin(x)"
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert " ^" in text


def test_bad_prompt():
    kernel = get_kernel(GnuplotKernel)
    # Anything other than 'gnuplot> '
    # is a bad prompt
    code = "set multiplot"
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert "warning" in text.lower()


def test_data_block():
    kernel = get_kernel(GnuplotKernel)

    # Good data block
    code = """
$DATA << EOD
# x y
1 1
2 2
3 3
4 4
EOD
plot $DATA
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert text.count("Display Data") == 1
    clear_log_text(kernel)

    # Badly terminated data block
    bad_code = """
$DATA << EOD
# x y
1 1
2 2
3 3
4 4
EODX
plot $DATA
    """
    kernel.do_execute(bad_code)
    text = get_log_text(kernel)
    assert "Error" in text
    clear_log_text(kernel)

    # Good code should work after the bad_code
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert text.count("Display Data") == 1


def test_do_for_loop():
    kernel = get_kernel(GnuplotKernel)
    code = """
    do for [t=0:2] {
      plot x**t t sprintf("x^%d",t)
    }
    """
    kernel.do_execute(code)
    text = get_log_text(kernel)
    assert text.count("Display Data") == 3


# magics #

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
    kernel.line_magics["gnuplot"] = gmagic
    kernel.cell_magics["gnuplot"] = gmagic

    # inline output
    code = """%%gnuplot
    plot cos(x)
    """
    kernel.do_execute(code)
    assert "Display Data" in get_log_text(kernel)
    clear_log_text(kernel)

    # file output
    kernel.call_magic("%gnuplot pngcairo size 560,420")
    code = """%%gnuplot
    set output 'cosine.png'
    plot cos(x)
    """
    kernel.do_execute(code)
    assert Path("cosine.png").exists()
    clear_log_text(kernel)

    remove_files("cosine.png")


def test_reset_cell_magic():
    kernel = get_kernel(GnuplotKernel)

    # Use reset statements that have testable effect
    code = """%%reset
    set output 'sine+cosine.png'
    plot sin(x) + cos(x)
    """
    kernel.call_magic(code)
    assert not Path("sine+cosine.png").exists()

    code = """
    unset key
    """
    kernel.do_execute(code)
    assert Path("sine+cosine.png").exists()

    remove_files("sine+cosine.png")


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
    kernel.call_magic("%reset")
    code = """
    unset key
    """
    kernel.do_execute(code)
    assert not Path("sine+sine.png").exists()

    # Bad inline backend
    # metakernel messes this exception!!
    # with assert_raises(ValueError):
    #     kernel.call_magic('%gnuplot inline qt')


# fixture tests #
def test_remove_files():
    """
    This test create a file. Next test tests that it
    is deleted
    """
    filename = "antigravit.txt"
    # Create file
    # make sure it exis
    with open(filename, "w"):
        pass

    assert Path(filename).exists()

    remove_files(filename)

    assert not Path(filename).exists()
