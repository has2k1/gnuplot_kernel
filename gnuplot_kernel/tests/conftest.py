import os
import pytest

try:
    FileNotFoundError
except NameError:
    # Python 2
    FileNotFoundError = OSError


def remove_files(*filenames):
    """
    Return a fixture that removes the files created
    during the test
    """

    @pytest.fixture()
    def _remove_files(request):
        yield _remove_files

        for filename in filenames:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    return _remove_files
