import sys
import re
import os.path
import uuid

from IPython.display import Image, SVG
from metakernel import MetaKernel, ProcessMetaKernel, pexpect, u
from metakernel.process_metakernel import TextOutput

from .replwrap import GnuplotREPLWrapper, PROMPT
from .exceptions import GnuplotError

# This is the only place that the version is
# specified
__version__ = '0.4.0'

# name of the command i.e first token
CMD_RE = re.compile(r'^\s*(\w+)\s?')
# "set multiplot" and abbreviated variants
MULTI_RE = re.compile(r'\s*set\s+multip(?:l|lo|lot)?')
# "unset multiplot" and abbreviated variants
UNMULTI_RE = re.compile(r'\s*uns(?:e|et)?\s+multip(?:l|lo|lot)?')
PLOT_CMDS = {
    'plot', 'plo', 'pl', 'p',
    'splot', 'splo', 'spl', 'sp',
    'replot', 'replo', 'repl', 'rep',
}
# "set output" and abbreviated variants
SET_OUTPUT_RE = re.compile(
    r'\s*set\s+o(?:u|ut|utp|utpu|utput)?(?:\s+|$)'
)

# "unset output" and abbreviated variants
UNSET_OUTPUT_RE = re.compile(
    r'\s*uns(?:e|et)?\s+o(?:u|ut|utp|utpu|utput)?\s*'
)


# funtions to recognise gnuplot statements that determine
# how we add temporary files for the images shown by jupyter
def is_set_output(stmt):
    """
    Return True if stmt is a 'set output' statement
    """
    m = re.match(SET_OUTPUT_RE, stmt)
    return True if m else False


def is_unset_output(stmt):
    """
    Return True if stmt is an 'unset output' statement
    """
    m = re.match(UNSET_OUTPUT_RE, stmt)
    return True if m else False


def is_set_multiplot(stmt):
    """
    Return True if stmt is a plot statement
    """
    m = re.match(MULTI_RE, stmt)
    return True if m else False


def is_unset_multiplot(stmt):
    """
    Return True if stmt is a plot statement
    """
    m = re.match(UNMULTI_RE, stmt)
    return True if m else False


def is_plot(stmt):
    """
    Return True if stmt is a plot statement
    """
    m = re.match(CMD_RE, stmt)
    if m:
        return m.group(1) in PLOT_CMDS
    return False


class GnuplotKernel(ProcessMetaKernel):
    implementation = 'Gnuplot Kernel'
    implementation_version = __version__
    language = 'gnuplot'
    language_version = '5.0'
    banner = 'Gnuplot Kernel'
    language_info = {
        'mimetype': 'text/x-gnuplot',
        'name': 'gnuplot',
        'file_extension': '.gp',
        'codemirror_mode': 'Octave',
        'help_links': MetaKernel.help_links,
    }
    kernel_json = {
        'argv': [sys.executable,
                 '-m', 'gnuplot_kernel',
                 '-f', '{connection_file}'],
        'display_name': 'gnuplot',
        'language': 'gnuplot',
        'name': 'gnuplot',
    }

    inline_plotting = True
    reset_code = ''
    _first = True
    _image_files = []
    _error = False

    def bad_prompt_warning(self):
        """
        Print warning if the prompt is not 'gnuplot>'
        """
        if not self.wrapper.prompt.startswith('gnuplot>'):
            msg = ("Warning: The prompt is currently set "
                   "to '{}'".format(self.wrapper.prompt))
            print(msg)

    def do_execute_direct(self, code):
        # We wrap the real function so that gnuplot_kernel can
        # give a message when an exception occurs. Without
        # this, an exception happens silently
        try:
            return self._do_execute_direct(code)
        except Exception as err:
            print(f"Error: {err}")
            raise err

    def _do_execute_direct(self, code):
        """
        Execute gnuplot code
        """
        if self._first:
            self._first = False
            self.handle_plot_settings()

        if self.inline_plotting:
            code = self.add_inline_image_statements(code)

        success = True

        try:
            result = super(GnuplotKernel,
                           self).do_execute_direct(code, silent=True)
        except GnuplotError as e:
            result = TextOutput(e.message)
            success = False

        if self.reset_code:
            super(GnuplotKernel, self).do_execute_direct(
                self.reset_code, silent=True)

        if self.inline_plotting:
            if success:
                self.display_images()
            self.delete_image_files()

        self.bad_prompt_warning()

        # No empty strings
        return result if (result and result.output) else None

    def add_inline_image_statements(self, code):
        """
        Add 'set output ...' before every plotting statement

        This is what powers inline plotting
        """
        # Ensure that there are no stale images
        self.delete_image_files()

        def set_output_inline(lines):
            filename = self.get_image_filename()
            if filename:
                lines.append("set output '{}'".format(filename))

        # We automatically create an output file for the following
        # cases if the user has not created one.
        #    - before every every plot statement that is not
        #      inside a multiplot block
        #    - before every multiplot block

        lines = []
        sm = StateMachine()
        is_joined_stmt = False
        for stmt in code.splitlines():
            sm.transition(stmt)
            add_inline_plot = (
                sm.prev_cur in (
                    ('none', 'plot'),
                    ('none', 'multiplot'),
                    ('plot', 'plot')
                )
                and not is_joined_stmt
            )
            if add_inline_plot:
                set_output_inline(lines)

            lines.append(stmt)
            is_joined_stmt = stmt.strip().endswith('\\')

        # Make gnuplot flush the output
        if not lines[-1].endswith('\\'):
            lines.append('unset output')
        code = '\n'.join(lines)
        return code

    def get_image_filename(self):
        """
        Create file to which gnuplot will write the plot

        Returns the filename.
        """
        # we could use tempfile.NamedTemporaryFile but we do not
        # want to create the file, gnuplot will create it.
        # Later on when we check if the file exists we know
        # whodunnit.
        settings = self.plot_settings
        filename = '/tmp/gnuplot-inline-{}.{}'.format(
            uuid.uuid1(),
            settings['format'])
        filename = filename
        self._image_files.append(filename)
        return filename

    def display_images(self):
        """
        Display images if gnuplot wrote to them
        """
        settings = self.plot_settings
        if self.inline_plotting:
            if settings['format'] == 'svg':
                _Image = SVG
            else:
                _Image = Image

        for filename in self._image_files:
            try:
                size = os.path.getsize(filename)
            except FileNotFoundError:
                size = 0

            if not size:
                msg = (
                    "Failed to read and display image file from gnuplot."
                    "May be you have plotted to a non interactive terminal."
                )
                print(msg)
                continue

            im = _Image(filename)
            self.Display(im)

    def delete_image_files(self):
        """
        Delete the image files
        """
        # After display_images(), the real images are
        # no longer required.
        for filename in self._image_files:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

        self._image_files = []

    def makeWrapper(self):
        """
        Start gnuplot and return wrapper around the REPL
        """
        if pexpect.which('gnuplot'):
            program = 'gnuplot'
        elif pexpect.which('gnuplot.exe'):
            program = 'gnuplot.exe'
        else:
            raise Exception("gnuplot not found.")

        # We don't want help commands getting stuck,
        # use a non interactive PAGER
        if pexpect.which('env') and pexpect.which('cat'):
            command = 'env PAGER=cat {}'.format(program)
        else:
            command = program

        d = dict(cmd_or_spawn=command,
                 prompt_regex=u('\w*> $'),
                 prompt_change_cmd=None)
        wrapper = GnuplotREPLWrapper(**d)
        # No sleeping before sending commands to gnuplot
        wrapper.child.delaybeforesend = 0
        return wrapper

    def do_shutdown(self, restart):
        """
        Exit the gnuplot process and any other underlying stuff
        """
        self.wrapper.exit()
        super(GnuplotKernel, self).do_shutdown(restart)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ''
        res = self.do_execute_direct('help %s' % obj)
        text = res.output.strip().rstrip(PROMPT)
        self.bad_prompt_warning()
        return text

    def handle_plot_settings(self):
        """
        Handle the current plot settings

        This is used by the gnuplot line magic. The plot magic
        is innadequate.
        """
        settings = self.plot_settings
        if ('termspec' not in settings or
                not settings['termspec']):
            settings['termspec'] = ('pngcairo size 385, 256'
                                    ' font "Arial,10"')
        if ('format' not in settings or
                not settings['format']):
            settings['format'] = 'png'

        self.inline_plotting = settings['backend'] == 'inline'

        cmd = 'set terminal {}'.format(settings['termspec'])
        self.do_execute_direct(cmd)


class StateMachine:
    """
    Track context given gnuplot statements

    This is used to help us tell when to add inline commands
    so that gnuplot can create inline images for the notebook
    """
    states = ['none', 'plot', 'output', 'multiplot', 'output_multiplot']
    previous = 'none'
    _current = 'none'

    @property
    def prev_cur(self):
        return (self.previous, self.current)

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        self.previous = self._current
        self._current = value

    def transition(self, stmt):
        lookup = {
            s: getattr(self, f'transition_from_{s}')
            for s in self.states
        }
        _transition = lookup[self.current]
        self.previous = self._current
        return _transition(stmt)

    def transition_from_plot(self, stmt):
        if self.current == 'output':
            self.current = 'none'
        elif self.current == 'plot':
            if is_plot(stmt):
                self.current = 'plot'
            elif is_set_output(stmt):
                self.current = 'output'
            else:
                self.current = 'none'

    def transition_from_none(self, stmt):
        if is_plot(stmt):
            self.current = 'plot'
        elif is_set_output(stmt):
            self.current = 'output'
        elif is_set_multiplot(stmt):
            self.current = 'multiplot'

    def transition_from_output(self, stmt):
        if is_plot(stmt):
            self.current = 'plot'
        elif is_set_multiplot(stmt):
            self.current = 'output_multiplot'
        elif is_unset_output(stmt):
            self.current = 'none'

    def transition_from_multiplot(self, stmt):
        if is_unset_multiplot(stmt):
            self.current = 'none'

    def transition_from_output_multiplot(self, stmt):
        if is_unset_multiplot(stmt):
            self.previous = self.current
            self.current = 'output'
