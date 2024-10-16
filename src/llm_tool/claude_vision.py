import anthropic
from dotenv import load_dotenv, find_dotenv
from llm_tool.image_handlers import add_image_data_to_conversation

load_dotenv(find_dotenv()) # Loads ANTHROPIC_API_KEY from .env

def claude_vision_conversation(
    parsed_file_contents: dict, 
    base_path: str,
    config: dict,
    ) -> str:

    client = anthropic.Anthropic()

    conversation = parsed_file_contents['conversation']
    rehydrated_conversation = add_image_data_to_conversation(conversation,base_path)

    # return rehydrated_conversation

    message = client.messages.create(
        model=config['model_name'],
        system=config['system_msg'],
        max_tokens=config['model_options'].pop('max_tokens',4096),
        messages= rehydrated_conversation,
        **config['model_options']
    )

    response = message.content[0].text
    formatted_response = "\n# %Assistant\n\n" + response
    return formatted_response