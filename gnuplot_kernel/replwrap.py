import re
import textwrap
import signal

from metakernel import REPLWrapper
from metakernel.pexpect import TIMEOUT
from .exceptions import GnuplotError

CRLF = '\r\n'
ERROR_REs = [re.compile(r'^\s*\^\s*\n')]
NO_BLOCK = ''
PROMPT = 'gnuplot>'
PROMPT_RE = re.compile(r'^\s*gnuplot>\s*$')


class GnuplotREPLWrapper(REPLWrapper):
    # The prompt after the commands run
    prompt = ''
    _blocks = {
        'data': {
            'start_re': re.compile(r'^\$\w+\s+<<\s*(?P<end>\w+)$'),
            'end_re': re.compile(r'^(?P<end>\w+)$')
        }
    }
    _current_block = NO_BLOCK

    def exit(self):
        """
        Exit the gnuplot process
        """
        try:
            self._force_prompt(timeout=.01)
        except GnuplotError:
            return self.child.kill(signal.SIGKILL)

        self.sendline('exit')

    def is_error_output(self, text):
        """
        Return True if text is recognised as error text
        """
        for pattern in ERROR_REs:
            if pattern.match(text):
                return True
        return False

    def validate_input(self, code):
        """
        Deal with problematic input

        Raises GnuplotError if it cannot deal with it.
        """
        if code.endswith('\\'):
            raise GnuplotError("Do not execute code that "
                               "endswith backslash.")

        # Do not get stuck in the gnuplot process
        code = code.replace('\\\n', ' ')
        return code

    def send(self, cmd):
        self.child.send(cmd + '\r')

    def _force_prompt(self, timeout=30, n=4):
        """
        Force prompt
        """
        quick_timeout = .05

        if timeout < quick_timeout:
            quick_timeout = timeout

        def quick_prompt():
            try:
                self._expect_prompt(timeout=quick_timeout)
                return True
            except TIMEOUT:
                return False

        def patient_prompt():
            try:
                self._expect_prompt(timeout=timeout)
                return True
            except TIMEOUT:
                return False

        # Eagerly try to get a prompt quickly,
        # If that fails wait a while
        for i in range(n):
            if quick_prompt():
                break

            # Probably stuck in help output
            if self.child.before:
                self.send(self.child.linesep)
        else:
            # Probably long computation going on
            if not patient_prompt():
                msg = ("gnuplot prompt failed to return in "
                       "in {} seconds").format(timeout)
                raise GnuplotError(msg)

    def _end_of_block(self, stmt, end_string):
        """
        Detect the end of block statements

        Parameters
        ----------
        stmt : str
            Statement to be executed by gnuplot repl

        Returns
        -------
        end_string : str
            Terminal string for the current block.
        """
        pattern_re = self._blocks[self._current_block]['end_re']
        m = pattern_re.match(stmt)
        if m:
            if m.group('end') == end_string:
                return True
        return False

    def _start_of_block(self, stmt):
        """
        Detect the start of block statements

        Parameters
        ----------
        stmt : str
            Statement to be executed by gnuplot repl
        Returns
        -------
        block_type : str
            Name of the block that has been detected.
            Returns an empty string if none has been detected.
        end_string : str
            Terminal string for the block that has been detected.
            Returns an empty string if none has been detected.
        """
        # These are used to detect the end of the block
        block_type = NO_BLOCK
        end_string = ''
        for _type, regexps in self._blocks.items():
            m = re.match(regexps['start_re'], stmt)
            if m:
                block_type = _type
                end_string = m.group('end')
                break
        return block_type, end_string

    def _splitlines(self, code):
        """
        Split the code into lines that will be run
        """
        # Statements in a block are not followed by a prompt, this
        # confuses the repl processing. We detect a block and concatenate
        # it into single line so that after executing the line we can
        # get a prompt.
        lines = []
        block_lines = []
        end_string = ''
        stmts = code.splitlines()
        for stmt in stmts:
            if self._current_block:
                block_lines.append(stmt)
                if self._end_of_block(stmt, end_string):
                    self._current_block = NO_BLOCK
                    block_lines.append('')
                    block = '\n'.join(block_lines)
                    lines.append(block)
                    block_lines = []
                    end_string = ''
            else:
                block_name, end_string = self._start_of_block(stmt)
                if block_name:
                    self._current_block = block_name
                    block_lines.append(stmt)
                else:
                    lines.append(stmt)

        if self._current_block:
            msg = 'Error: {} block not terminated correctly.'.format(
                self._current_block)
            self._current_block = NO_BLOCK
            raise GnuplotError(msg)

        return lines

    def run_command(self, code, timeout=-1, stream_handler=None,
                    stdin_handler=None):
        """
        Run code

        This overrides the baseclass method to allow for
        input validation and error handling.
        """
        code = self.validate_input(code)

        # Split up multiline commands and feed them in bit-by-bit
        stmts = self._splitlines(code)
        output_lines = []
        for line in stmts:
            self.send(line)
            self._force_prompt()

            # Removing any crlfs makes subsequent
            # processing cleaner
            retval = self.child.before.replace(CRLF, '\n')
            self.prompt = self.child.after
            if self.is_error_output(retval):
                msg = '{}\n{}'.format(
                    line, textwrap.dedent(retval))
                raise GnuplotError(msg)

            # Sometimes block stmts like datablocks make the
            # the prompt leak into the return value
            retval = retval.replace(PROMPT,  '').strip(' ')
            output_lines.append(retval)

        output = ''.join(output_lines)
        return output
