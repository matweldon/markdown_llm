CONFIG = {
    "model": 'claude-3-5-sonnet-20240620',
    "system": "",
    "options": {
        "max_tokens": 2048,
        #"temperature": 0.5
    }
}

# Set the command to open the text editor
# Either:
# A template string including {markdown_filepath}
#   the filepath will be inserted in the template
# A bare string
#   the filepath will be added to the end
EDITOR = "code -r -g {markdown_filepath}:3" # Open at line 3