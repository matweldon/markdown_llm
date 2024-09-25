from llm_tool.parser import parse_conversation, parse_markdown_with_yaml
from llm_tool.llm_conversation import llm_conversation
from llm_tool.claude_vision import claude_vision_conversation
import os
import sys

def main(markdown_filepath):
    base_path = os.path.dirname(os.path.abspath(markdown_filepath))

    with open(markdown_filepath, 'r') as file:
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

    with open(markdown_filepath,'a') as file:
        file.write('\n' + str(response))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python -m llm_tool <path_to_markdown_file>")
        sys.exit(1)
    
    main(sys.argv[1])