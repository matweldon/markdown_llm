import anthropic
from dotenv import load_dotenv, find_dotenv
from llm_tool.parser import add_image_data_to_conversation

load_dotenv(find_dotenv()) # Loads ANTHROPIC_API_KEY from .env

def claude_vision_conversation(parsed_file_contents,base_path):

    client = anthropic.Anthropic()

    conversation = parsed_file_contents['conversation']
    rehydrated_conversation = add_image_data_to_conversation(conversation,base_path)

    # return rehydrated_conversation

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages= rehydrated_conversation
    )

    response = message.content[0].text
    formatted_response = "\n# %Assistant\n\n" + response
    return formatted_response