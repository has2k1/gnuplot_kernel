import re
import textwrap
import signal

from metakernel import REPLWrapper
from metakernel.pexpect import TIMEOUT
from .exceptions import GnuplotError

CRLF = '\r\n'
ERROR_REs = [re.compile(r'^\s*\^\s*\n')]
BAD_OUTPUT_REs = [re.compile(r'Closing /tmp/gnuplot-inline')]


class GnuplotREPLWrapper(REPLWrapper):
    prompt = ''
    current_error = ''

    def exit(self):
        """
        Exit the gnuplot process
        """
        # If nothing is terribly wrong a couple
        # of crlfs should ensure we are at the
        # prompt
        self.sendline(CRLF)
        self.sendline(CRLF)

        try:
            self._expect_prompt(timeout=.1)
        except TIMEOUT:
            return self.child.kill(signal.SIGKILL)

        self.sendline('exit')

    def is_error(self, text):
        """
        Return True if text is recognised as error text
        """
        for pattern in ERROR_REs:
            if pattern.match(text):
                return True
        return False

    def filter_output(self, text):
        """
        Sink hole for unwanted output
        """
        for pattern in BAD_OUTPUT_REs:
            if pattern.match(text):
                return ''
        return text

    def validate_input(self, code):
        """
        Deal with problematic input
        """
        if code.endswith('\\'):
            self.current_error = ("Do not execute code that "
                                  "endswith backslash.")
            raise GnuplotError()

        # Do not get stuck in the gnuplot process
        code = code.replace('\\\n', ' ')
        return code

    def run_command(self, code, timeout=-1, stream_handler=None):
        """
        Run code

        This overrides the baseclass method to allow for
        input validation and error handling that is.
        """
        self.current_error = ''
        code = self.validate_input(code)
        # Split up multiline commands and feed them in bit-by-bit
        stmts = code.splitlines()
        output = ''
        for line in stmts:
            self.sendline(line)
            self._expect_prompt()
            # Removing any crlfs makes subsequent
            # processing cleaner
            retval = self.child.before.replace(CRLF, '\n')
            retval = self.filter_output(retval)
            self.prompt = self.child.after
            if self.is_error(retval):
                s = textwrap.dedent(retval)
                self.current_error = '{}\n{}'.format(line, s)
                raise GnuplotError()
            output += retval

        return output
