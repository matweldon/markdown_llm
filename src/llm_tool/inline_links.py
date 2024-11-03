from pathlib import Path
from llm_tool.paths import resolve_existing_filepath
import os

def _convert_link_to_full_text(link_chunk: dict) -> dict:
    """
    Convert a link chunk to a text chunk by reading the file contents.

    Parameters
    ----------
    link_chunk : dict
        A dictionary containing the link information.

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
    >>> link_chunk = {"type": "link", "link": "path/to/example.txt"}
    >>> _convert_link_to_full_text(link_chunk)
    {'type': 'text', 'text': 'File contents here'}
    """
    absolute_path = Path(link_chunk.get("link")).resolve()
    
    file_contents = absolute_path.read_text().strip()

    return {"type": "text", "text": file_contents}
        


def replace_links_with_file_contents(conversation: list[dict]) -> list[dict]:
    """
    Replace link chunks in a conversation with the contents of the linked files.

    Parameters
    ----------
    conversation : list of dict
        A list of conversation turns, where each turn is a dictionary
        containing 'role' and 'content' keys.

    Returns
    -------
    list of dict
        The conversation with link chunks replaced by text chunks
        containing the file contents.

    Examples
    --------
    >>> conversation = [
    ...     {
    ...         "role": "user",
    ...         "content": [
    ...             {"type": "text", "text": "Hello"},
    ...             {"type": "link", "link": "example.txt"}
    ...         ]
    ...     }
    ... ]
    >>> replace_links_with_file_contents(conversation)
    [{'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}, {'type': 'text', 'text': 'File contents here'}]}]
    """
    for turn in conversation:
        if turn['role'] == 'user':
            turn['content'] = [
                 _convert_link_to_full_text(chunk)
                 if chunk['type'] == 'link' 
                 else chunk 
                 for chunk in turn['content']
                 ]

    return conversation

