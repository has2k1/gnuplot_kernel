import sys
from itertools import chain
from pathlib import Path
import uuid

from IPython.display import Image, SVG
from metakernel import MetaKernel, ProcessMetaKernel, pexpect
from metakernel.process_metakernel import TextOutput

from .statement import STMT
from .exceptions import GnuplotError
from .replwrap import GnuplotREPLWrapper, PROMPT_RE, PROMPT_REMOVE_RE
from .utils import get_version


IMG_COUNTER = '__gpk_img_index'
IMG_COUNTER_FMT = '%03d'


class GnuplotKernel(ProcessMetaKernel):
    """
    GnuplotKernel
    """
    implementation = 'Gnuplot Kernel'
    implementation_version = get_version('gnuplot_kernel')
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
            result = super().do_execute_direct(code, silent=True)
        except GnuplotError as e:
            result = TextOutput(e.message)
            success = False

        if self.reset_code:
            super().do_execute_direct(self.reset_code, silent=True)

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
        # "set output sprintf('foobar.%d.png', counter);"
        # "counter=counter+1"
        def set_output_inline(lines):
            tpl = self.get_image_filename()
            if tpl:
                cmd = (
                    f"set output sprintf('{tpl}', {IMG_COUNTER});"
                    f"{IMG_COUNTER}={IMG_COUNTER}+1"
                )
                lines.append(cmd)

        # We automatically create an output file for the following
        # cases if the user has not created one.
        #    - before every plot statement that is not in a
        #      multiplot block
        #    - before every multiplot block

        lines = []
        sm = StateMachine()
        is_joined_stmt = False
        for line in code.splitlines():
            stmt = STMT(line)
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
        fmt = self.plot_settings['format']
        filename = Path(
            f'/tmp/gnuplot-inline-{uuid.uuid1()}'
            f'.{IMG_COUNTER_FMT}'
            f'.{fmt}'
        )
        self._image_files.append(filename)
        return filename

    def iter_image_files(self):
        """
        Iterate over the image files
        """
        it = chain(*[
            sorted(f.parent.glob(f.name.replace(IMG_COUNTER_FMT, '*')))
            for f in self._image_files
        ])
        return it

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

        for filename in self.iter_image_files():
            try:
                size = filename.stat().st_size
            except FileNotFoundError:
                size = 0

            if not size:
                msg = (
                    "Failed to read and display image file from gnuplot."
                    "Possibly:\n"
                    "1. You have plotted to a non interactive terminal.\n"
                    "2. You have an invalid expression."
                )
                print(msg)
                continue

            im = _Image(str(filename))
            self.Display(im)

    def delete_image_files(self):
        """
        Delete the image files
        """
        # After display_images(), the real images are
        # no longer required.
        for filename in self.iter_image_files():
            try:
                filename.unlink()
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

        d = dict(
            cmd_or_spawn=command,
            prompt_regex=PROMPT_RE,
            prompt_change_cmd=None
        )
        wrapper = GnuplotREPLWrapper(**d)
        # No sleeping before sending commands to gnuplot
        wrapper.child.delaybeforesend = 0
        return wrapper

    def do_shutdown(self, restart):
        """
        Exit the gnuplot process and any other underlying stuff
        """
        self.wrapper.exit()
        super().do_shutdown(restart)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ''
        res = self.do_execute_direct('help %s' % obj)
        text = PROMPT_REMOVE_RE.sub('', res.output)
        self.bad_prompt_warning()
        return text

    def reset_image_counter(self):
        # Incremented after every plot image, and used in the
        # plot image filename. Makes plotting in loops do_for
        # loops work
        cmd = f'{IMG_COUNTER}=0'
        self.do_execute_direct(cmd)

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
        self.reset_image_counter()


class StateMachine:
    """
    Track context given gnuplot statements

    This is used to help us tell when to inject commands (i.e. set output)
    that for inline plotting in the notebook.
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
            if stmt.is_plot():
                self.current = 'plot'
            elif stmt.is_set_output():
                self.current = 'output'
            else:
                self.current = 'none'

    def transition_from_none(self, stmt):
        if stmt.is_plot():
            self.current = 'plot'
        elif stmt.is_set_output():
            self.current = 'output'
        elif stmt.is_set_multiplot():
            self.current = 'multiplot'

    def transition_from_output(self, stmt):
        if stmt.is_plot():
            self.current = 'plot'
        elif stmt.is_set_multiplot():
            self.current = 'output_multiplot'
        elif stmt.is_unset_output():
            self.current = 'none'

    def transition_from_multiplot(self, stmt):
        if stmt.is_unset_multiplot():
            self.current = 'none'

    def transition_from_output_multiplot(self, stmt):
        if stmt.is_unset_multiplot():
            self.previous = self.current
            self.current = 'output'
