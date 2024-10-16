import pytest
from llm_tool.parser import _parse_user_content_types, parse_conversation, _remove_commented_text

# Tests for _parse_user_content_types

def test_parse_user_content_types_basic():
    content = "Hello [link](url) ![image](img.png)"
    result = _parse_user_content_types(content)
    assert result == [
        {'type': 'text', 'text': 'Hello'},
        {'type': 'link', 'link': 'url'},
        {'type': 'image', 'source': 'img.png'}
    ]

def test_parse_user_content_types_multiple():
    content = "Text1 [link1](url1) Text2 ![image1](img1.png) [link2](url2) Text3 ![image2](img2.png)"
    result = _parse_user_content_types(content)
    assert result == [
        {'type': 'text', 'text': 'Text1'},
        {'type': 'link', 'link': 'url1'},
        {'type': 'text', 'text': 'Text2'},
        {'type': 'image', 'source': 'img1.png'},
        {'type': 'link', 'link': 'url2'},
        {'type': 'text', 'text': 'Text3'},
        {'type': 'image', 'source': 'img2.png'}
    ]

def test_parse_user_content_types_empty():
    assert _parse_user_content_types("") == []

def test_parse_user_content_types_whitespace():
    assert _parse_user_content_types("   ") == []

def test_parse_user_content_types_only_text():
    assert _parse_user_content_types("Just text") == [{'type': 'text', 'text': 'Just text'}]

def test_parse_user_content_types_only_links():
    content = "[link1](url1) [link2](url2)"
    assert _parse_user_content_types(content) == [
        {'type': 'link', 'link': 'url1'},
        {'type': 'link', 'link': 'url2'}
    ]

def test_parse_user_content_types_only_images():
    content = "![img1](url1) ![img2](url2)"
    assert _parse_user_content_types(content) == [
        {'type': 'image', 'source': 'url1'},
        {'type': 'image', 'source': 'url2'}
    ]

def test_parse_user_content_types_newlines():
    content = "Text1\n[link](url)\nText2\n![image](img.png)"
    result = _parse_user_content_types(content)
    assert result == [
        {'type': 'text', 'text': 'Text1'},
        {'type': 'link', 'link': 'url'},
        {'type': 'text', 'text': 'Text2'},
        {'type': 'image', 'source': 'img.png'}
    ]

# Test for _remove_commented_text

def test_remove_commented_text():
    content_end = "This is a string of\n text with a comment<!--llm IGNORED llm-->"
    content_middle = "This is a string of\n<!--llm IGNORED llm--> text with a comment"
    content_beginning = "<!--llm IGNORED llm-->This is a string of\n text with a comment"
    content = "This is a string of\n text with a comment"
    assert content == _remove_commented_text(content_end)
    assert content == _remove_commented_text(content_middle)
    assert content == _remove_commented_text(content_beginning)

# Tests for parse_conversation

def test_parse_conversation_basic():
    content = "# %User\nHello [link](url)\n# %Assistant\nHi there\n# %User\n![image](img.png)"
    result = parse_conversation(content)
    assert result['conversation'] == [
        {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}, {'type': 'link', 'link': 'url'}]},
        {'role': 'assistant', 'content': 'Hi there'},
        {'role': 'user', 'content': [{'type': 'image', 'source': 'img.png'}]}
    ]
    assert result['metadata']['has_images']


def test_parse_conversation_with_comment():
    content = "# %User\nHello [link](url)\n\n<!--llm IGNORED llm-->\n# %Assistant\nHi there\n# %User\n![image](img.png)"
    result = parse_conversation(content)
    assert result['conversation'] == [
        {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}, {'type': 'link', 'link': 'url'}]},
        {'role': 'assistant', 'content': 'Hi there'},
        {'role': 'user', 'content': [{'type': 'image', 'source': 'img.png'}]}
    ]
    assert result['metadata']['has_images']

def test_parse_conversation_single_turn():
    content = "# %User\nHello"
    result = parse_conversation(content)
    assert result['conversation'] == [{'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}]}]
    assert not result['metadata']['has_images']

def test_parse_conversation_empty():
    assert parse_conversation("")['conversation'] == []

def test_parse_conversation_whitespace_between_turns():
    content = "# %User\nHello\n\n# %Assistant\nHi\n\n# %User\nBye"
    result = parse_conversation(content)
    result_conversation = result['conversation']
    assert len(result_conversation) == 3
    assert result_conversation[0]['role'] == 'user'
    assert result_conversation[1]['role'] == 'assistant'
    assert result_conversation[2]['role'] == 'user'
    assert not result['metadata']['has_images']

def test_parse_conversation_unicode():
    content = "# %User\nHello 世界 [link](url)\n# %Assistant\nこんにちは"
    result = parse_conversation(content)
    assert result['conversation'] == [
        {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello 世界'}, {'type': 'link', 'link': 'url'}]},
        {'role': 'assistant', 'content': 'こんにちは'}
    ]
    assert not result['metadata']['has_images']

# Edge cases for both functions

def parse_conversation_conversation(file_contents):
    return parse_conversation(file_contents)['conversation']

@pytest.mark.parametrize("func", [_parse_user_content_types, parse_conversation_conversation])
def test_edge_cases(func):
    assert func("") == []
    assert func("   ") == []
    assert func("\n\n\n") == []
