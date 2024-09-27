from llm_tool.parser import parse_conversation, parse_markdown_with_yaml
from llm_tool.llm_conversation import llm_conversation
from llm_tool.claude_vision import claude_vision_conversation
from llm_tool import EDITOR
import os
import sys
import string
import subprocess

def main(markdown_filepath=None):

    if markdown_filepath is None:
        if len(sys.argv) != 2:
            print("Usage: llmmd <path_to_markdown_file>")
            return 1
        markdown_filepath = sys.argv[1]
    
    path_type = validate_file_path(markdown_filepath)
    if path_type == 'exists':
        read_and_write_response(markdown_filepath)
    
    if path_type == 'new':
        with open(markdown_filepath,'x') as f:
            f.write("# %User\n")
        # Open EDITOR at line 3
        commandlist = EDITOR.split() + [f"{markdown_filepath}:3"]
        subprocess.run(commandlist)


def read_and_write_response(validated_filepath):

    base_path = os.path.dirname(os.path.abspath(validated_filepath))

    with open(validated_filepath, 'r') as file:
        content = file.read()

    config, content_body = parse_markdown_with_yaml(content)
    parsed_file_contents = parse_conversation(content_body)

    if parsed_file_contents['metadata']['has_images']:
        print('Handling images by using Anthropic API')
        response = claude_vision_conversation(
            parsed_file_contents=parsed_file_contents,
            base_path=base_path,
            config=config,
            )
    else:
        response = llm_conversation(parsed_file_contents,config)

    with open(validated_filepath,'a') as file:
        file.write('\n' + str(response))

def validate_file_path(path):

    # Split the path into directory and filename
    directory, filename = os.path.split(path)
    
    # Check if the directory exists
    if not os.path.exists(directory):
        raise ValueError("Directory does not exist")
    
    # Check if we have write permission in the directory
    if not os.access(directory, os.W_OK):
        raise ValueError("No write permission in the directory")
    
    # Check if the filename is valid
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    if not all(c in valid_chars for c in filename):
        raise ValueError("Invalid characters in filename")
    
    # Check if the file already exists
    if os.path.exists(path) and os.path.isfile(path):
        return "exists"
    
    return "new"

if __name__ == '__main__':
    sys.exit(main())