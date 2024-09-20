from llm_tool.parser import parse_conversation
from llm_tool.llm_conversation import llm_conversation
from llm_tool.claude_vision import claude_vision_conversation
import os
import sys

def main(markdown_filepath):
    base_path = os.path.dirname(os.path.abspath(markdown_filepath))

    with open(markdown_filepath, 'r') as file:
        content = file.read()
    parsed_file_contents = parse_conversation(content)

    if parsed_file_contents['metadata']['has_images']:
        print('Handling images by using Anthropic API')
        response = claude_vision_conversation(parsed_file_contents,base_path)
    else:
        response = llm_conversation(parsed_file_contents)

    with open(markdown_filepath,'a') as file:
        file.write('\n' + str(response))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python -m llm_tool <path_to_markdown_file>")
        sys.exit(1)
    
    main(sys.argv[1])