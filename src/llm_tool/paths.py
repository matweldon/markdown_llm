from pathlib import Path
import string
import os

def validate_file_path(path: str | Path) -> str:
    """
    Validate a file path and return its type.

    Parameters
    ----------
    path : str | Path
        The file path to validate.

    Returns
    -------
    str
        'new' if the file doesn't exist, 'exists' if it does.

    Raises
    ------
    ValueError
        If the directory doesn't exist, lacks write permission, or the filename is invalid.

    Examples
    --------
    >>> validate_file_path('existing_file.txt')
    'exists'
    >>> validate_file_path('new_file.txt')
    'new'
    >>> validate_file_path('/nonexistent/path/file.txt')
    Traceback (most recent call last):
        ...
    ValueError: Directory does not exist
    """
    path = Path(path).resolve()
    directory = path.parent
    filename = path.name

    if not directory.exists():
        raise ValueError("Directory does not exist")

    if not os.access(directory, os.W_OK):
        raise ValueError("No write permission in the directory")

    valid_chars = "-_.() " + string.ascii_letters + string.digits
    if not all(c in valid_chars for c in filename):
        raise ValueError("Invalid characters in filename")

    return "exists" if path.is_file() else "new"
