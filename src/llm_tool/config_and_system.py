from collections.abc import Iterable
import yaml
from pathlib import Path
import os
from platformdirs import user_config_dir

def merge_configs(configs: Iterable[dict]):
    """Create config dict from list of configs.

    Higher priority at end of list or iterable. Passing a
    value of None unsets a value set previously.

    Args:
        configs (Iterable[dict]): A list of config dicts

    Returns:
        dict: A merged config file
    """
    merged_config = dict()

    for config in configs:
        for key, value in config.items():
            if value is None:
                merged_config.pop(key,None)
            else:
                merged_config[key] = value

    return merged_config


def get_config(configs: Iterable[dict]):
    """Get config from the YAML config locations in order
    of priority.

    This function processes the configs in order. The config at
    the end of the iterable will have priority. For example,
    pass them in the order [SYSTEM,USER,PROJECT,FILE] so that
    the file configs will supercede others.

    Any key-value pair where the value is None (null in yaml) will
    unset a value set in a lower-priority config (ie. the 
    key-value pair will be deleted).

    Args:
        config (Iterable of dicts): dicts containing the model name,
        templated system message and other options.

    Returns:
        Tuple[str,str,dict]: A tuple containing the model name,
        the reconstituted system message including snippets,
        and a dictionary containing remaining options
    """

    merged_config = merge_configs(configs)
    model_name = merged_config.get('model')
    template_system_msg = merged_config.get('system')
    model_options = merged_config.get('options')

    sys_snippets = {
        k: v for k, v in merged_config.items() 
        if k.startswith('sys_')
        }

    system_msg = template_system_msg.format_map(sys_snippets)

    return model_name, system_msg, model_options


def get_or_make_user_config_path() -> None:
    """Prints user config path

    If the folder doesn't exist it is created.

    Use the command llmd-config-path to run this module.

    For example, to copy a local yaml to the user config dir,
    run:
    > cp llmd_config.yaml "$(llmd-config-path)"
    """
    config_dir = os.getenv("llmd_config_dir",user_config_dir("llmd"))
    config_dir = Path(config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = config_dir / "config.yaml"
    print(config_path)

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
