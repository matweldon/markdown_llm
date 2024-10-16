import pytest
import tempfile
import os
from pathlib import Path
from llm_tool.inline_links import _convert_link_to_full_text, replace_links_with_file_contents

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        file1 = Path(tmpdirname) / "file1.txt"
        file1.write_text("hello")
        file2 = Path(tmpdirname) / "file2.txt"
        file2.write_text("world")
        yield tmpdirname

def test_convert_link_to_full_text(temp_dir):
    result = _convert_link_to_full_text({"type": "link", "link": "file1.txt"}, temp_dir)
    assert result == {"type": "text", "text": "hello"}

def test_convert_link_to_full_text_non_existent(temp_dir):
    with pytest.raises(ValueError):
        _convert_link_to_full_text({"type": "link", "link": "non_existent.txt"}, temp_dir)

def test_replace_links_with_file_contents(temp_dir):
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Text1"},
                {"type": "link", "link": "file1.txt"},
                {"type": "text", "text": "Text2"},
                {"type": "link", "link": "file2.txt"},
            ]
        }
    ]
    result = replace_links_with_file_contents(conversation, temp_dir)
    expected = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Text1"},
                {"type": "text", "text": "hello"},
                {"type": "text", "text": "Text2"},
                {"type": "text", "text": "world"},
            ]
        }
    ]
    assert result == expected

def test_replace_links_with_file_contents_multiple_turns(temp_dir):
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Text1"},
                {"type": "link", "link": "file1.txt"},
            ]
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "Response"}]
        },
        {
            "role": "user",
            "content": [
                {"type": "link", "link": "file2.txt"},
            ]
        }
    ]
    result = replace_links_with_file_contents(conversation, temp_dir)
    expected = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Text1"},
                {"type": "text", "text": "hello"},
            ]
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "Response"}]
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "world"},
            ]
        }
    ]
    assert result == expected

def test_replace_links_with_file_contents_no_links(temp_dir):
    conversation = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Text1"}]
        }
    ]
    result = replace_links_with_file_contents(conversation, temp_dir)
    assert result == conversation

