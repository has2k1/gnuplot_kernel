import re
import textwrap
import signal

from metakernel import REPLWrapper
from metakernel.pexpect import TIMEOUT
from .exceptions import GnuplotError

CRLF = '\r\n'
ERROR_REs = [re.compile(r'^\s*\^\s*\n')]


class GnuplotREPLWrapper(REPLWrapper):
    # The prompt after the commands run
    prompt = ''

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

    def run_command(self, code, timeout=-1, stream_handler=None,
                    stdin_handler=None):
        """
        Run code

        This overrides the baseclass method to allow for
        input validation and error handling.
        """
        code = self.validate_input(code)

        # Split up multiline commands and feed them in bit-by-bit
        stmts = code.splitlines()
        output = []
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

            output.append(retval)

        return ''.join(output)
