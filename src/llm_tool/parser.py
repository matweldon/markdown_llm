import re
import yaml
from llm_tool.paths import resolve_existing_filepath
import os


def parse_conversation(file_contents: str,base_path: str | os.PathLike = ".", ignore_images=False,ignore_links=False) -> list[dict]:
    """Parse a conversation into user and assistant turns

    Args:
        file_contents (str): The contents of the markdown file after removal
           of the YAML header.
        base_path (str | os.PathLike): The base path to resolve relative links.
        ignore_images (bool)
        ignore_links (bool)

    Returns:
        list[dict]: A list of turns, where turns have either a role of
         'user' or 'assistant', with content.

    Examples:
        >>> content = "# User\\nHello\\n[file](path.txt)\\n![img](img.png)\\n# Assistant\\nHi there"
        >>> parse_conversation(content)
        [{'role': 'user', 'content': [
            {'type': 'text', 'text': 'Hello'}, 
            {'type': 'link', 'link': '/path/to/path.txt'}, 
            {'type': 'image', 'source': '/path/to/img.png'}]
          }, 
         {'role': 'assistant', 'content': 'Hi there'}
        ]
    """
    pattern = r'# %(User|Assistant)\n(.*?)(?=# %User|# %Assistant|$)'

    pruned_file_contents = _remove_commented_text(file_contents)

    conversation = []
    for role, content in re.findall(pattern, pruned_file_contents, re.DOTALL):
        conversation.append({
            "role": role.lower(),
            "content": _parse_user_content_types(
                content,
                base_path = base_path,
                ignore_images=ignore_images,
                ignore_links=ignore_links
                ) if role == 'User' else content.strip()
        })
    
    metadata = {'has_images': _has_images(conversation)}

    return {'conversation':conversation, 'metadata': metadata}


def parse_markdown_with_yaml(markdown_content: str) -> tuple[dict,str]:
    """Remove YAML header from markdown document and return as dict.

    If there is a YAML header, parse it and return it as a dict, and also
    return the body of the markdown document.
    If there is no YAML header, it returns an empty dict and the body of
    the markdown document.

    Args:
        markdown_content (str): The contents of the markdown doc as a string

    Returns:
        dict: Contents of the YAML header, or empty dict
        str: Body of the markdown doc
    """
    # Regular expression to match the YAML header
    yaml_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    # Find the YAML header
    match = yaml_pattern.match(markdown_content)
    
    if match:
        # Extract the YAML content
        yaml_content = match.group(1)
        
        try:
            # Parse the YAML content into a dictionary
            yaml_dict = yaml.safe_load(yaml_content)
            
            # Get the body of the Markdown document
            markdown_body = markdown_content[match.end():]
            
            print("Using YAML header options.")
            return yaml_dict, markdown_body
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return dict(), markdown_content
    else:
        return dict(), markdown_content


def _remove_commented_text(file_contents,pattern=r'<!--llm.*?llm-->'):
    """Remove commented text from a string"""
    return re.sub(pattern,'',file_contents,flags=re.DOTALL)


    
def _parse_user_content_types(content: str, base_path: str | os.PathLike = ".", ignore_images=False,ignore_links=False) -> list[dict]:
    """Find and split text, links and images in a user turn"""
    chunk_pattern = r'(?P<text>.*?)(?:(?P<link>(?<!!)\[.*?\]\((?P<linkpath>.*?)\))|(?P<image>!\[.*?\]\((?P<imagepath>.*?)\))|$)'
    chunks = []
    for match in re.finditer(chunk_pattern, content, re.DOTALL):
        if match.group('text').strip():
            chunks.append({'type': 'text', 'text': match.group('text').strip()})
        if match.group('link') and not ignore_links:
            chunks.append({'type': 'link', 'link': str(resolve_existing_filepath(match.group('linkpath'),base_path))})
        if match.group('image') and not ignore_images:
            chunks.append({'type': 'image', 'source': str(resolve_existing_filepath(match.group('imagepath'),base_path))})
    return chunks

def _has_images(conversation: list[dict]) -> bool:
    """Check if a conversation contains any image elements"""
    return any(
        any(chunk.get('type') == 'image' for chunk in turn['content'])
        if isinstance(turn['content'], list) else False
        for turn in conversation
    )