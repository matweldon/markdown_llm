from pathlib import Path
from llm_tool.paths import validate_file_path
import os

def _convert_link_to_full_text(link_chunk: dict,base_path: str | os.PathLike) -> dict:
    """
    Convert a link chunk to a text chunk by reading the file contents.

    Parameters
    ----------
    link_chunk : dict
        A dictionary containing the link information.
    base_path : str or os.PathLike
        The base path to resolve relative links.

    Returns
    -------
    dict
        A dictionary with the file contents as text.

    Raises
    ------
    ValueError
        If the file does not exist.

    Examples
    --------
    >>> base_path = '/path/to/files'
    >>> link_chunk = {"type": "link", "link": "example.txt"}
    >>> _convert_link_to_full_text(link_chunk, base_path)
    {'type': 'text', 'text': 'File contents here'}
    """
    absolute_path = Path(base_path) / link_chunk.get("link", 'new')
    absolute_path = absolute_path.resolve()
    new_or_exists = validate_file_path(absolute_path)
    if new_or_exists == 'new':
        raise ValueError("File does not exist")
    
    file_contents = absolute_path.read_text().strip()

    return {"type": "text", "text": file_contents}
        


def replace_links_with_file_contents(conversation: list[dict], base_path: str | os.PathLike) -> list[dict]:
    """
    Replace link chunks in a conversation with the contents of the linked files.

    Parameters
    ----------
    conversation : list of dict
        A list of conversation turns, where each turn is a dictionary
        containing 'role' and 'content' keys.
    base_path : str or os.PathLike
        The base path to resolve relative links.

    Returns
    -------
    list of dict
        The conversation with link chunks replaced by text chunks
        containing the file contents.

    Examples
    --------
    >>> base_path = '/path/to/files'
    >>> conversation = [
    ...     {
    ...         "role": "user",
    ...         "content": [
    ...             {"type": "text", "text": "Hello"},
    ...             {"type": "link", "link": "example.txt"}
    ...         ]
    ...     }
    ... ]
    >>> replace_links_with_file_contents(conversation, base_path)
    [{'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}, {'type': 'text', 'text': 'File contents here'}]}]
    """
    for turn in conversation:
        if turn['role'] == 'user':
            turn['content'] = [
                 _convert_link_to_full_text(chunk,base_path)
                 if chunk['type'] == 'link' 
                 else chunk 
                 for chunk in turn['content']
                 ]

    return conversation

