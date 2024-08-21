import llm
import os
import sys
import re
import base64
import anthropic
from dotenv import load_dotenv
from pathlib import Path

def parse_conversation(file_contents):
    pattern = r'# %(User|Assistant)\n(.*?)(?=# %User|# %Assistant|$)'
    pattern_image = r'!\[.*?\]\((.*?)\)'
    matches = re.findall(pattern, file_contents, re.DOTALL)
    
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

def get_base64(filepath: str | os.PathLike):
    with open(filepath, 'rb') as f:
        img_bin = f.read()
    img_base64 = base64.b64encode(img_bin).decode('utf-8')
    return img_base64

def rehydrate_image(rel_path,base_path):
    """Convert rel_path into full base64-encoded image

    Args:
        rel_path (str): A relative path to an image file
        base_path (str): An absolute path from which the rel path is relative
    """
    absolute_path = os.path.join(base_path,rel_path)
    mtype = Path(rel_path).suffix[1:]
    if mtype == 'jpg':
        mtype = 'jpeg'
    return {
            "type": "base64",
            "media_type": f"image/{mtype}",
            "data": get_base64(absolute_path)
        }

def add_image_data_to_conversation(conversation,base_path):
    for turn in conversation:
        if turn['role'] == 'user':
            for chunk in turn['content']:
                if chunk['type'] == 'image':
                    chunk['source'] = rehydrate_image(chunk['source'],base_path)
    return conversation
