"""
Useful functions
"""

from importlib.metadata import version


def get_version(package):
    """
    Return the package version

    Raises PackageNotFoundError if package is not installed
    """
    # The goal of this function to avoid circular imports if the
    # version is required in 2 or more spot before the package has
    # been fully installed
    return version(package)
