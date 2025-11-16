import llm
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv()) # Loads any API key env variables set in .env


def _create_fake_response(model, prompt_text, response_text, system=None):
    """
    Recreate the functionality of llm.Response.fake() which was removed in llm 0.18.

    This helper function constructs a Response object that appears to be from a
    completed API call, allowing us to reconstruct conversation history.

    Args:
        model: The llm Model instance
        prompt_text: The user's prompt text
        response_text: The assistant's response text
        system: Optional system message

    Returns:
        llm.Response: A fake response object with the given content
    """
    prompt_obj = llm.Prompt(
        prompt_text,
        model=model,
        system=system,
    )

    response_obj = llm.Response(
        prompt=prompt_obj,
        model=model,
        stream=False,
    )

    # Set internal state to make it look like a completed response
    response_obj._done = True
    response_obj._chunks = [response_text]

    return response_obj


def chunk_user_assistant_turns(conversation):
    """
    Convert a parsed conversation into user/assistant turn pairs.

    Takes a conversation structure with separate user and assistant turns and
    chunks them into pairs where each pair contains a user message and optionally
    an assistant response. The last pair may not have an assistant response if
    it represents a new unanswered prompt.

    Args:
        conversation (list): List of conversation turns, where each turn is a dict
            with 'role' ('user' or 'assistant') and 'content'. User content is a
            list of items with 'type' and content data (text, images, etc.).
            Assistant content is a string.

    Returns:
        list: List of dicts, each containing:
            - 'user': String with user's message (text and image paths joined with \\n\\n)
            - 'assistant': String with assistant's response (may be absent in last item)

    Example:
        >>> conversation = [
        ...     {'role': 'user', 'content': [{'type': 'text', 'text': 'Hello'}]},
        ...     {'role': 'assistant', 'content': 'Hi there!'},
        ...     {'role': 'user', 'content': [{'type': 'text', 'text': 'How are you?'}]}
        ... ]
        >>> chunk_user_assistant_turns(conversation)
        [
            {'user': 'Hello', 'assistant': 'Hi there!'},
            {'user': 'How are you?'}
        ]
    """
    result = []
    current_pair = {}

    for turn in conversation:
        if turn['role'] == 'user':
            if current_pair:
                result.append(current_pair)
                current_pair = {}
            
            user_content = []
            for item in turn['content']:
                if item['type'] == 'text':
                    user_content.append(item['text'])
                elif item['type'] == 'image':
                    user_content.append(item['source'])
            current_pair['user'] = '\n\n'.join(user_content)
        
        elif turn['role'] == 'assistant':
            current_pair['assistant'] = turn['content']

    if current_pair:
        result.append(current_pair)

    return result


def llm_conversation(parsed_file_contents: dict, config: dict) -> str:
    """
    Process a conversation from a markdown file and get an LLM response to a new prompt.

    This function reconstructs the conversation history using fake responses, then
    sends a new prompt to the LLM to continue the conversation. If there's no new
    prompt (the conversation already has a response to the last user message), it
    returns an empty string.

    Args:
        parsed_file_contents (dict): Parsed markdown file containing:
            - 'conversation': List of conversation turns with role and content
        config (dict): Configuration containing:
            - 'model_name': Name of the LLM model to use
            - 'system_msg': System message for the LLM
            - 'model_options': Additional options to pass to the model (e.g., max_tokens)

    Returns:
        str: Formatted response from the LLM as markdown (e.g., "\\n# %Assistant\\n\\nResponse text"),
            or empty string if there's no new prompt to respond to.

    Note:
        This function prints "No new prompts." to stdout when there's no new prompt.
    """
    chunked_conversation = chunk_user_assistant_turns(parsed_file_contents['conversation'])

    model = llm.get_model(config['model_name'])
    conversation = model.conversation()

    if 'assistant' not in chunked_conversation[-1].keys():
        new_prompt = chunked_conversation.pop()

        conversation.responses += [
            _create_fake_response(
                model=model,
                prompt_text=turn['user'],
                response_text=turn['assistant'],
                system=config['system_msg'],
            )
            for turn in chunked_conversation
        ]

        new_response = conversation.prompt(
            new_prompt['user'],
            system=config['system_msg'],
            **config['model_options'],
        )
        new_formatted_response = f"\n# %Assistant\n\n{new_response}"
    else:
        print('No new prompts.')
        new_formatted_response = ''

    return new_formatted_response





