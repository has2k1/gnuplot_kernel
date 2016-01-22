import os

try:
    FileNotFoundError
except NameError:
    # Python 2
    FileNotFoundError = OSError


def remove_files(filenames):
    """
    Return a function at remove files

    This is meant to be used as a teardown
    function.
    """
    if not isinstance(filenames, (tuple, list)):
        filenames = (filenames,)

    def _remove_files():
        for filename in filenames:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    return _remove_files
