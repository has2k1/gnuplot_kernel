"""
Recognising gnuplot statements
"""
import re

# name of the command i.e first token
CMD_RE = re.compile(
    r"^\s*"
    r"(?P<cmd>"
    r"\w+"   # The command
    r")"
    r"\s?"
)

# plot statements
PLOT_RE = re.compile(
    r"^\s*"
    r"(?P<plot_cmd>"
    r"plot|plo|pl|p|"
    r"splot|splo|spl|sp|"
    r"replot|replo|repl|rep"
    r")"
    r"\s?"
)

# "set multiplot" and abbreviated variants
SET_MULTIPLE_RE = re.compile(
    r"\s*"
    r"set"
    r"\s+"
    r"multip(?:lot|lo|l)?\b"
    r"\b"
)

# "unset multiplot" and abbreviated variants
UNSET_MULTIPLE_RE = re.compile(
    r"\s*"
    r"(?:unset|unse|uns)"
    r"\s+"
    r"multip(?:lot|lo|l)?\b"
    r"\b"
)


# "set output" and abbreviated variants
SET_OUTPUT_RE = re.compile(
    r"\s*"
    r"set"
    r"\s+"
    r"(?:output|outpu|outp|out|ou|o)"
    r"(?:\s+|$)"
)

# "unset output" and abbreviated variants
UNSET_OUTPUT_RE = re.compile(
    r"\s*"
    r"(?:unset|unse|uns)"
    r"\s+"
    r"(?:output|outpu|outp|out|ou|o)"
    r"(?:\s+|$)"
)


class STMT(str):
    """
    A gnuplot statement
    """

    def is_set_output(self):
        """
        Return True if stmt is a 'set output' statement
        """
        return bool(SET_OUTPUT_RE.match(self))

    def is_unset_output(self):
        """
        Return True if stmt is an 'unset output' statement
        """
        return bool(UNSET_OUTPUT_RE.match(self))

    def is_set_multiplot(self):
        """
        Return True if stmt is a "set multiplot" statement
        """
        return bool(SET_MULTIPLE_RE.match(self))

    def is_unset_multiplot(self):
        """
        Return True if stmt is a "unset multiplot" statement
        """
        return bool(UNSET_MULTIPLE_RE.match(self))

    def is_plot(self):
        """
        Return True if stmt is a plot statement
        """
        return bool(PLOT_RE.match(self))
