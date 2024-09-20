%%prompt%%

I want to make a python utility to parse a markdown file with images into an API call to the Anthropic Claude API, and then write the resulting response back into the same markdown file. I've already created a tool to handle text without images using a third-party package, but now I have to use the Anthropic Python SDK directly because the package I was using can't handle images.

The markdown file will look like this:

```markdown
# Prompt

![image1](path/to/cats.png)

What is in this image?
```

The prompt could contain zero, one or multiple image links, and more than one chunk of text. I want to be able to call the utility from the command line by entering

`python -m llm_vision_tool path/to/markdown_file.md`

and the result will be that the LLM response is written back into the markdown file, for example:

```markdown
# Prompt

![image1](path/to/cats.png)

What is in this image?

# Response

The image shows three adorable kittens sitting together on what appears to be a white surface, possibly a car roof or a ledge...
```

The Anthropic Python API code to run this query and print the response would be:

```python
import os
import anthropic
import base64

client = anthropic.Anthropic()

image_path = 'data/cats.png'
prompt_text = 'What is in this image?'

def get_base64(filepath: str | os.PathLike):
    with open(filepath,'rb') as f:
        img_bin = f.read()
    img_base64 = base64.b64encode(img_bin).decode('utf-8')
    return img_base64

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=2048,
    messages= [
        {"role": "user", "content": [
            {"type": "image", "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": get_base64(image_path)
            }},
            {"type": "text", "text": prompt_text}
        ]
        }]
)

print(message.content)
```

I see the following difficulties that I'd like your help to solve:

* Recognising the prompt and parsing it into text chunks and the file path of the images
* Converting the relative path to the images into absolute paths depending on the location of the markdown file
* writing the response back to the markdown file


%%response%%

Certainly! I'd be happy to help you create a Python utility that can parse a markdown file with images, make an API call to Anthropic's Claude API, and write the response back to the same markdown file. Here's a script that should accomplish what you're looking for:

```python
import os
import sys
import re
import base64
import anthropic
from pathlib import Path

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
    images = re.findall(image_pattern, prompt)
    text_chunks = re.split(image_pattern, prompt)
    text_chunks = [chunk.strip() for chunk in text_chunks if chunk.strip()]

    return images, text_chunks

def create_message_content(images, text_chunks, base_path):
    content = []
    for i, (image, text) in enumerate(zip(images + [None], text_chunks)):
        if image:
            absolute_path = os.path.join(base_path, image)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{Path(image).suffix[1:]}",
                    "data": get_base64(absolute_path)
                }
            })
        if text:
            content.append({"type": "text", "text": text})
    return content

def main(markdown_file):
    base_path = os.path.dirname(os.path.abspath(markdown_file))
    images, text_chunks = parse_markdown(markdown_file)
    
    client = anthropic.Anthropic()
    
    message_content = create_message_content(images, text_chunks, base_path)
    
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
```

This script does the following:

1. It defines helper functions to get base64 encodings of images and to parse the markdown file.

2. The `parse_markdown` function extracts image paths and text chunks from the markdown content.

3. The `create_message_content` function prepares the content for the API call, converting relative image paths to absolute paths.

4. The `main` function orchestrates the process:
   - It parses the markdown file
   - Creates the API client
   - Prepares the message content
   - Makes the API call
   - Writes the response back to the markdown file

5. The script can be run from the command line as requested.

To use this script:

1. Save it as `llm_vision_tool.py` in a directory.
2. Create a `__main__.py` file in the same directory with the following content:

```python
from llm_vision_tool import main
import sys

if __name__ == "__main__":
    main(sys.argv[1])
```

3. You can then run the script from the command line as:

```
python -m llm_vision_tool path/to/markdown_file.md
```

This script handles the difficulties you mentioned:
- It recognizes the prompt and parses it into text chunks and image file paths.
- It converts relative image paths to absolute paths based on the location of the markdown file.
- It writes the response back to the markdown file, either appending it or replacing an existing response.

Make sure you have the `anthropic` package installed (`pip install anthropic`) and that you've set up your Anthropic API key as an environment variable (`ANTHROPIC_API_KEY`) before running the script.

%%prompt%%

This nearly works, but the function `create_message_content` assumes that images are interspersed with text chunks, and assumes that images are first. It might be the case that the prompt is something like this:

```markdown
# Prompt

![image1](path/to/image1.png)
![image2](path/to/image2.png)

Compare these two images.
```

Another problem is that the `text_chunks` returned by `parse_markdown` contain the image paths as well as the text chunks. I think you need a different regex to split at that without returning the file paths inside the parentheses.

%%response%%

You're absolutely right, and I apologize for those oversights. Let's refine the script to handle these cases more accurately. Here's an updated version that addresses both issues:

```python
import os
import sys
import re
import base64
import anthropic
from pathlib import Path

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
    images = re.findall(image_pattern, prompt)
    
    # Split text without including image markdown
    text_chunks = re.split(r'!\[.*?\]\(.*?\)', prompt)
    text_chunks = [chunk.strip() for chunk in text_chunks if chunk.strip()]

    return images, text_chunks

def create_message_content(images, text_chunks, base_path):
    content = []
    
    # Add text chunks and images in the order they appear
    i, j = 0, 0
    while i < len(text_chunks) or j < len(images):
        if i < len(text_chunks) and (j == len(images) or text_chunks[i].index < images[j].index):
            content.append({"type": "text", "text": text_chunks[i]})
            i += 1
        else:
            absolute_path = os.path.join(base_path, images[j])
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{Path(images[j]).suffix[1:]}",
                    "data": get_base64(absolute_path)
                }
            })
            j += 1
    
    return content

def main(markdown_file):
    base_path = os.path.dirname(os.path.abspath(markdown_file))
    images, text_chunks = parse_markdown(markdown_file)
    
    client = anthropic.Anthropic()
    
    message_content = create_message_content(images, text_chunks, base_path)
    
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
```

The key changes are:

1. In the `parse_markdown` function:
   - The regex for splitting text chunks has been updated to `r'!\[.*?\]\(.*?\)'`. This will split the text at image markdown without including the image paths in the text chunks.

2. The `create_message_content` function has been completely rewritten:
   - It now creates the content list by interleaving text chunks and images in the order they appear in the original markdown.
   - This handles cases where multiple images appear consecutively or where text appears before or after all images.

These changes should now correctly handle markdown files with any combination of text and images, including cases where multiple images appear consecutively or where all images appear before or after the text.

The rest of the script remains the same. This version should now correctly parse your markdown files and create the appropriate message content for the Anthropic API call, regardless of the order or number of text chunks and images.