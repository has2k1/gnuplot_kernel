import os
from contextlib import contextmanager
from pathlib import Path

os.environ["JUPYTER_PLATFORM_DIRS"] = "1"


@contextmanager
def ensure_deleted(*paths: str):
    """
    Ensures the given file paths are deleted when the block exits
    
    Parameters
    ----------
    *paths : pathlib.Path
        One or more file paths
    """
    paths = tuple(Path(path) for path in paths)

    try:
        yield paths if len(paths) > 1 else paths[0]
    finally:
        for path in paths:
            Path(path).unlink()
