import re
import yaml


def remove_commented_text(file_contents,pattern=r'<!--llm.*?llm-->'):
    """Remove commented text from a string"""
    return re.sub(pattern,'',file_contents,flags=re.DOTALL)

def parse_conversation(file_contents):
    """Parse a conversation into user and assistant turns

    Args:
        file_contents (str): The contents of the markdown file after removal
           of the YAML header.

    Returns:
        dict: A dictionary with two slots: conversation and metadata.
        The conversation is a list of turns, where turns have either a role of
         'User' or 'Assistant', with content.
    """
    pruned_file_contents = remove_commented_text(file_contents)

    pattern = r'# %(User|Assistant)\n(.*?)(?=# %User|# %Assistant|$)'
    pattern_image = r'!\[.*?\]\((.*?)\)'
    matches = re.findall(pattern, pruned_file_contents, re.DOTALL)
    
    conversation = []
    has_images = False
    for role, content in matches:
        if role == 'User':
            content_images = re.findall(pattern_image,content)
            content_images_and_text = re.split(pattern_image,content)
            content_images_and_text = [chunk.strip() for chunk in content_images_and_text if chunk.strip()]
            chunks = []
            for chunk in content_images_and_text:
                if chunk in content_images:
                    has_images = True
                    chunks.append({'type':'image','source':chunk})
                else:
                    chunks.append({'type':'text','text':chunk})
        else:
            content = content.strip()
            chunks = content
        conversation.append({
            "role": role.lower(),
            "content": chunks
        })
    
    metadata = {'has_images':has_images}
    return {'conversation':conversation,'metadata':metadata}

def parse_markdown_with_yaml(markdown_content) -> tuple[dict,str]:
    """Remove YAML header from markdown document and return as dict.

    If there is a YAML header, parse it and return it as a dict, and also
    return the body of the markdown document.

    Args:
        markdown_content (str): The contents of the markdown doc as a string

    Returns:
        dict: Contents of the YAML header
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
            return None, markdown_content
    else:
        return None, markdown_content

