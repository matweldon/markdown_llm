from llm_tool.parser import parse_conversation, parse_markdown_with_yaml
from llm_tool.llm_conversation import llm_conversation
from llm_tool.claude_vision import claude_vision_conversation
from llm_tool.paths import validate_file_path
from llm_tool import EDITOR
import os
import re
import sys
from pathlib import Path
import string
import subprocess

md_header = """---
model: claude-3-5-sonnet-20240620
system: '{sys_python_prefs}'
options:
  max_tokens: 4096
---

# %User

"""

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
            f.write(md_header)
        # Open EDITOR at line 2
        editor_command_list = make_editor_command(markdown_filepath,EDITOR)
        subprocess.run(editor_command_list)


def make_editor_command(filepath,editor_command):
    if re.search(r'{markdown_filepath}',editor_command):
        full_editor_command = editor_command.format(markdown_filepath=filepath)
        editor_command_list = full_editor_command.split()
    else:
        editor_command_list = editor_command.split() + [filepath]
    return editor_command_list


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


if __name__ == '__main__':
    sys.exit(main())