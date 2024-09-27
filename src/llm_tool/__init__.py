CONFIG = {
    "model": 'claude-3-5-sonnet-20240620',
    "system": "",
    "options": {
        "max_tokens": 2048,
        #"temperature": 0.5
    }
}

# Set the command to open the text editor
# The filepath will be appended to the end of this command
# This will currently only work for the code command
# because of the line number (see __main__.py)
EDITOR = 'code -r -g'