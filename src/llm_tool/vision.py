import os
import sys
import re
import base64
import anthropic
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def get_base64(filepath: str | os.PathLike):
    with open(filepath, 'rb') as f:
        img_bin = f.read()
    img_base64 = base64.b64encode(img_bin).decode('utf-8')
    return img_base64

def parse_markdown(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Split content into prompt and response (if exists)
    parts = content.split('# Response', 1)
    prompt = parts[0].strip()

    # Parse images and text from prompt
    image_pattern = r'!\[.*?\]\((.*?)\)'
    # split_pattern = r'!\[.*?\]\(.*?\)'
    images = re.findall(image_pattern, prompt)
    text_and_image = re.split(image_pattern, prompt)
    # text_no_image = re.split(split_pattern,prompt)
    text_and_image = [chunk.strip() for chunk in text_and_image if chunk.strip()]
    chunks = []
    for chunk in text_and_image:
        if chunk in images:
            chunks.append(('image',chunk))
        else:
            chunks.append(('text',chunk))

    # text_chunks = list(set(text_chunks).difference(set(images)))
    return chunks

def create_message_content(chunks, base_path):
    content = []
    for (chunk_type,chunk) in chunks:
        if chunk_type == 'image':
            absolute_path = os.path.join(base_path, chunk)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{Path(chunk).suffix[1:]}",
                    "data": get_base64(absolute_path)
                }
            })
        if chunk_type == 'text':
            content.append({"type": "text", "text": chunk})
    return content

def main(markdown_file):
    base_path = os.path.dirname(os.path.abspath(markdown_file))
    chunks = parse_markdown(markdown_file)
    
    client = anthropic.Anthropic()
    
    message_content = create_message_content(chunks, base_path)
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": message_content}
        ]
    )
    
    response = message.content[0].text
    
    # Write response back to markdown file
    with open(markdown_file, 'r+') as f:
        content = f.read()
        if '# Response' in content:
            content = content.split('# Response')[0]
        f.seek(0)
        f.write(content.strip() + f'\n\n# Response\n\n{response}\n')
        f.truncate()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m llm_vision_tool <path_to_markdown_file>")
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    main(markdown_file)
