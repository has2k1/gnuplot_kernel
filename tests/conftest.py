import os


def remove_files(*filenames):
    """
    Remove the files created during the test
    """
    for filename in filenames:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
