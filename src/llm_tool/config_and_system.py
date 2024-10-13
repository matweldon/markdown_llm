from llm_tool import CONFIG

def get_config(config: dict | None = None):
    """Get config from the YAML header or file.

    This function processes the config from the YAML header, using
    the default configs, and reconstitutes a system message.

    Args:
        config (dict, optional): A dict containing the model name,
        templated system message and other options. Defaults to None.

    Returns:
        Tuple[str,str,dict]: A tuple containing the model name,
        the reconstituted system message including snippets,
        and a dictionary containing remaining options
    """
    if config == None:
        config = dict()
    
    model_name = config.get('model',CONFIG.get('model'))
    template_system_msg = config.get('system',CONFIG.get('system'))
    model_options = config.get('options',CONFIG.get('options'))

    sys_prototypes = {
        k: v for k, v in CONFIG.items() 
        if k.startswith('sys_')
        }

    system_msg = template_system_msg.format_map(sys_prototypes)

    return model_name, system_msg, model_options