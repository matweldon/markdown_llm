import os
from platformdirs import user_config_dir
from llm_tool.config_and_system import load_config_or_empty

llmd_config_dir = os.getenv("llmd_config_dir",user_config_dir(appname="llmd"))

DEFAULT_CONFIG = {
    "model": 'claude-3-5-sonnet-20240620',
    "system": "{sys_python_prefs}",
    "options": {
        "max_tokens": 4096,
        #"temperature": 0.5
    },
    "sys_python_prefs": """
    These are my preferences for python:
    * Public python functions and methods should have numpy docstrings
    * docstrings should have examples for doctest
    * For packaging questions, use pyproject.toml with setuptools
    * Add type hints to functions and methods
    * For type hints, don't use Union. Use the newer | syntax
    In answers adhere to these preferences but no need to refer back to them.

    Answers should be no longer than they need to be. If I've asked you to solve a problem, 
    don't give long explanations for your decisions. If I need explanations I'll ask for them.

    If I've asked you for options you can give reasons but be succinct.
    """,
    "editor_cmd": "code -r -g {markdown_filepath}:99999",
    #"editor_cmd": "vim +99999 {markdown_filepath}",
}

USER_CONFIG = load_config_or_empty(llmd_config_dir,'config.yaml')
PROJECT_CONFIG = load_config_or_empty(os.getcwd(),'llmd_config.yaml')

