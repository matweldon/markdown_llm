CONFIG = {
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

    If I've asked you for options you can give reasons them but be succinct.
    """
}

# Set the command to open the text editor
# Either:
# A template string including {markdown_filepath}
#   the filepath will be inserted in the template
# A bare string
#   the filepath will be added to the end
EDITOR = "code -r -g {markdown_filepath}:99999" # Open at last line
# EDITOR = "vim +99999"