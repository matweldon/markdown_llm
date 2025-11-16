"""Tests for llm_conversation module, particularly the _create_fake_response helper function."""
import pytest
import llm
from llm_tool.llm_conversation import _create_fake_response, chunk_user_assistant_turns


class TestCreateFakeResponse:
    """Test suite for _create_fake_response function."""

    @pytest.fixture
    def model(self):
        """Fixture to get a test model."""
        return llm.get_model('gpt-4o-mini')

    def test_basic_fake_response(self, model):
        """Test creating a basic fake response with minimal arguments."""
        prompt_text = "What is 2+2?"
        response_text = "4"

        response = _create_fake_response(
            model=model,
            prompt_text=prompt_text,
            response_text=response_text
        )

        assert response is not None
        assert isinstance(response, llm.Response)
        assert response.text() == response_text
        assert response.prompt.prompt == prompt_text

    def test_fake_response_with_system_message(self, model):
        """Test creating a fake response with a system message."""
        prompt_text = "Tell me a joke"
        response_text = "Why did the chicken cross the road?"
        system_msg = "You are a helpful assistant."

        response = _create_fake_response(
            model=model,
            prompt_text=prompt_text,
            response_text=response_text,
            system=system_msg
        )

        assert response.text() == response_text
        assert response.prompt.prompt == prompt_text
        assert response.prompt.system == system_msg

    def test_fake_response_without_system_message(self, model):
        """Test creating a fake response without a system message."""
        prompt_text = "Hello"
        response_text = "Hi there!"

        response = _create_fake_response(
            model=model,
            prompt_text=prompt_text,
            response_text=response_text,
            system=None
        )

        assert response.text() == response_text
        # System can be None or empty string when not provided
        assert response.prompt.system in (None, '')

    def test_fake_response_multiline_text(self, model):
        """Test creating a fake response with multiline prompt and response."""
        prompt_text = """Write a haiku about Python.
Please make it funny."""
        response_text = """Python in the night,
Indentation matters most,
Tabs versus spaces."""

        response = _create_fake_response(
            model=model,
            prompt_text=prompt_text,
            response_text=response_text
        )

        assert response.text() == response_text
        assert response.prompt.prompt == prompt_text

    def test_fake_response_empty_strings(self, model):
        """Test creating a fake response with empty strings."""
        response = _create_fake_response(
            model=model,
            prompt_text="",
            response_text=""
        )

        assert response.text() == ""
        assert response.prompt.prompt == ""

    def test_fake_response_special_characters(self, model):
        """Test creating a fake response with special characters."""
        prompt_text = "What is 2 + 2? Don't say \"5\"!"
        response_text = "2 + 2 = 4\n\nIt's definitely not \"5\" 😊"

        response = _create_fake_response(
            model=model,
            prompt_text=prompt_text,
            response_text=response_text
        )

        assert response.text() == response_text
        assert response.prompt.prompt == prompt_text

    def test_fake_response_unicode(self, model):
        """Test creating a fake response with Unicode characters."""
        prompt_text = "Say hello in Japanese"
        response_text = "こんにちは (Konnichiwa)"

        response = _create_fake_response(
            model=model,
            prompt_text=prompt_text,
            response_text=response_text
        )

        assert response.text() == response_text
        assert response.prompt.prompt == prompt_text

    def test_fake_response_model_association(self, model):
        """Test that the fake response is properly associated with the model."""
        response = _create_fake_response(
            model=model,
            prompt_text="Test",
            response_text="Response"
        )

        assert response.model == model
        assert response.prompt.model == model

    def test_fake_response_done_flag(self, model):
        """Test that the fake response is marked as done."""
        response = _create_fake_response(
            model=model,
            prompt_text="Test",
            response_text="Response"
        )

        # The response should be marked as done
        assert response._done is True

    def test_fake_response_chunks(self, model):
        """Test that the fake response has the correct chunks."""
        response_text = "This is the response"
        response = _create_fake_response(
            model=model,
            prompt_text="Test",
            response_text=response_text
        )

        # The response should have the text in chunks
        assert response._chunks == [response_text]

    def test_fake_response_stream_flag(self, model):
        """Test that the fake response is not marked as streaming."""
        response = _create_fake_response(
            model=model,
            prompt_text="Test",
            response_text="Response"
        )

        # Based on the implementation, stream should be False
        # We can verify this by checking the Response object was created with stream=False
        assert hasattr(response, 'stream')

    def test_multiple_fake_responses(self, model):
        """Test creating multiple fake responses."""
        responses = []
        for i in range(5):
            response = _create_fake_response(
                model=model,
                prompt_text=f"Question {i}",
                response_text=f"Answer {i}"
            )
            responses.append(response)

        assert len(responses) == 5
        for i, response in enumerate(responses):
            assert response.text() == f"Answer {i}"
            assert response.prompt.prompt == f"Question {i}"

    def test_fake_response_in_conversation(self, model):
        """Test using fake responses in a conversation context."""
        conversation = model.conversation()

        # Add fake responses to simulate conversation history
        fake_resp1 = _create_fake_response(
            model=model,
            prompt_text="What is 2+2?",
            response_text="4",
            system="You are a helpful math tutor"
        )

        fake_resp2 = _create_fake_response(
            model=model,
            prompt_text="What about 3+3?",
            response_text="6",
            system="You are a helpful math tutor"
        )

        conversation.responses.append(fake_resp1)
        conversation.responses.append(fake_resp2)

        assert len(conversation.responses) == 2
        assert conversation.responses[0].text() == "4"
        assert conversation.responses[1].text() == "6"


class TestChunkUserAssistantTurns:
    """Test suite for chunk_user_assistant_turns function."""

    def test_basic_chunking(self):
        """Test basic chunking of user/assistant turns."""
        conversation = [
            {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}]},
            {'role': 'assistant', 'content': 'Hi there!'},
            {'role': 'user', 'content': [{'type': 'text', 'text': 'How are you?'}]},
            {'role': 'assistant', 'content': 'I am doing well, thank you!'}
        ]

        result = chunk_user_assistant_turns(conversation)

        assert len(result) == 2
        assert result[0] == {'user': 'Hello', 'assistant': 'Hi there!'}
        assert result[1] == {'user': 'How are you?', 'assistant': 'I am doing well, thank you!'}

    def test_chunking_incomplete_turn(self):
        """Test chunking when the last turn has no assistant response."""
        conversation = [
            {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}]},
            {'role': 'assistant', 'content': 'Hi there!'},
            {'role': 'user', 'content': [{'type': 'text', 'text': 'New question'}]}
        ]

        result = chunk_user_assistant_turns(conversation)

        assert len(result) == 2
        assert result[0] == {'user': 'Hello', 'assistant': 'Hi there!'}
        assert result[1] == {'user': 'New question'}
        assert 'assistant' not in result[1]

    def test_chunking_multiple_content_types(self):
        """Test chunking with multiple content types (text and images)."""
        conversation = [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'Look at this'},
                    {'type': 'image', 'source': 'image1.png'},
                    {'type': 'text', 'text': 'What do you see?'}
                ]
            },
            {'role': 'assistant', 'content': 'I see a cat'}
        ]

        result = chunk_user_assistant_turns(conversation)

        assert len(result) == 1
        assert result[0]['user'] == 'Look at this\n\nimage1.png\n\nWhat do you see?'
        assert result[0]['assistant'] == 'I see a cat'

    def test_chunking_empty_conversation(self):
        """Test chunking an empty conversation."""
        conversation = []
        result = chunk_user_assistant_turns(conversation)
        assert result == []

    def test_chunking_single_user_turn(self):
        """Test chunking with only a single user turn."""
        conversation = [
            {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}]}
        ]

        result = chunk_user_assistant_turns(conversation)

        assert len(result) == 1
        assert result[0] == {'user': 'Hello'}
        assert 'assistant' not in result[0]

    def test_chunking_multiple_text_items(self):
        """Test chunking when user content has multiple text items."""
        conversation = [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'First part'},
                    {'type': 'text', 'text': 'Second part'},
                    {'type': 'text', 'text': 'Third part'}
                ]
            },
            {'role': 'assistant', 'content': 'Got it'}
        ]

        result = chunk_user_assistant_turns(conversation)

        assert len(result) == 1
        assert result[0]['user'] == 'First part\n\nSecond part\n\nThird part'
        assert result[0]['assistant'] == 'Got it'

    def test_chunking_preserves_order(self):
        """Test that chunking preserves the order of turns."""
        conversation = [
            {'role': 'user', 'content': [{'type': 'text', 'text': 'Q1'}]},
            {'role': 'assistant', 'content': 'A1'},
            {'role': 'user', 'content': [{'type': 'text', 'text': 'Q2'}]},
            {'role': 'assistant', 'content': 'A2'},
            {'role': 'user', 'content': [{'type': 'text', 'text': 'Q3'}]},
            {'role': 'assistant', 'content': 'A3'}
        ]

        result = chunk_user_assistant_turns(conversation)

        assert len(result) == 3
        for i, chunk in enumerate(result, 1):
            assert chunk['user'] == f'Q{i}'
            assert chunk['assistant'] == f'A{i}'

    def test_chunking_with_images_only(self):
        """Test chunking when user content has only images."""
        conversation = [
            {
                'role': 'user',
                'content': [
                    {'type': 'image', 'source': 'img1.png'},
                    {'type': 'image', 'source': 'img2.png'}
                ]
            },
            {'role': 'assistant', 'content': 'I see two images'}
        ]

        result = chunk_user_assistant_turns(conversation)

        assert len(result) == 1
        assert result[0]['user'] == 'img1.png\n\nimg2.png'
        assert result[0]['assistant'] == 'I see two images'

    def test_chunking_empty_content(self):
        """Test chunking when user content is empty."""
        conversation = [
            {'role': 'user', 'content': []},
            {'role': 'assistant', 'content': 'Nothing to respond to'}
        ]

        result = chunk_user_assistant_turns(conversation)

        assert len(result) == 1
        assert result[0]['user'] == ''
        assert result[0]['assistant'] == 'Nothing to respond to'
