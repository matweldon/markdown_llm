import yaml
from pathlib import Path

def load_config_or_empty(path: str, filename: str) -> dict:
    """
    Load a YAML file into a dict if it exists, otherwise return an empty dict.

    Parameters
    ----------
    path : str
        The directory path where the YAML file is located.
    filename : str
        The name of the YAML file.

    Returns
    -------
    dict
        The loaded YAML content as a dict, or an empty dict if the file doesn't exist.

    Examples
    --------
    >>> load_config_or_empty("/path/to/dir", "config.yaml")
    {'key': 'value'}
    >>> load_config_or_empty("/path/to/nonexistent", "missing.yaml")
    {}
    """
    file_path = Path(path) / filename

    if file_path.is_file() and file_path.suffix in {'.yaml', '.yml'}:
        with file_path.open('r') as f:
            config = yaml.safe_load(f)
    else:
        config = dict()
    if not isinstance(config,dict):
        config = dict()
    return config
