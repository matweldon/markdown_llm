from llm_tool import CONFIG

def get_config(config = None):
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