from collections.abc import Iterable

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