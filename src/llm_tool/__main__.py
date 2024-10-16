from llm_tool.parser import parse_conversation, parse_markdown_with_yaml
from llm_tool.inline_links import replace_links_with_file_contents
from llm_tool.llm_conversation import llm_conversation
from llm_tool.claude_vision import claude_vision_conversation
from llm_tool.paths import validate_file_path
from llm_tool import DEFAULT_CONFIG, USER_CONFIG, PROJECT_CONFIG
from llm_tool.config_and_system import get_config, merge_configs
from pathlib import Path
from os import PathLike
import re
import sys
import subprocess
from datetime import date

md_header = """---
model: claude-3-5-sonnet-20240620
system: '{sys_python_prefs}'
date: {todays_date}
options:
  max_tokens: 4096
---

# %User

""".format(
    sys_python_prefs="{sys_python_prefs}", # A clunky hack to partially evaluate the template
    todays_date=date.today().strftime("%d %B %Y"),
)

EDITOR = (
    merge_configs([DEFAULT_CONFIG,USER_CONFIG,PROJECT_CONFIG])
    .get('editor_cmd')
    )

def main(markdown_filepath: str | PathLike[str] | None = None):

    if markdown_filepath is None:
        if len(sys.argv) != 2:
            print("Usage: llmd <path_to_markdown_file>")
            return 1
        markdown_filepath = sys.argv[1]
    
    path_type = validate_file_path(markdown_filepath)
    if path_type == 'exists':
        print("File exists: writing response in place")
        read_and_write_response(markdown_filepath)
    
    if path_type == 'new':
        with open(markdown_filepath,'x') as f:
            f.write(md_header)
        # Open EDITOR at line 2
        editor_command_list = make_editor_command(markdown_filepath,EDITOR)
        subprocess.run(editor_command_list)


def make_editor_command(filepath: str | PathLike[str], editor_command: str) -> list[str]:
    if re.search(r'{markdown_filepath}',editor_command):
        full_editor_command = editor_command.format(markdown_filepath=filepath)
        editor_command_list = full_editor_command.split()
    else:
        editor_command_list = editor_command.split() + [filepath]
    return editor_command_list


def read_and_write_response(validated_filepath: str | PathLike[str]):

    base_path = Path(validated_filepath).resolve().parent

    with open(validated_filepath, 'r') as file:
        content = file.read()

    file_config, content_body = parse_markdown_with_yaml(content)


    config = get_config(
            [
                DEFAULT_CONFIG,
                USER_CONFIG,
                PROJECT_CONFIG,
                file_config,
            ]
        )
    
    parsed_conversation = parse_conversation(
        content_body,
        ignore_images=config['ignore_images'],
        ignore_links=config['ignore_links'],
        )
    
    if not config['ignore_links']:
        parsed_conversation['conversation'] = replace_links_with_file_contents(parsed_conversation['conversation'],base_path)

    if parsed_conversation['metadata']['has_images']:
        print('Handling images by using Anthropic API')
        response = claude_vision_conversation(
            parsed_file_contents=parsed_conversation,
            base_path=base_path,
            config=config,
            )
    else:
        response = llm_conversation(parsed_conversation,config)

    with open(validated_filepath,'a') as file:
        file.write('\n' + str(response))


if __name__ == '__main__':
    sys.exit(main())