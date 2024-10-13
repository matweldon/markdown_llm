import anthropic
from dotenv import load_dotenv, find_dotenv
from llm_tool.image_handlers import add_image_data_to_conversation
from llm_tool.config_and_system import get_config
from llm_tool import CONFIG

load_dotenv(find_dotenv()) # Loads ANTHROPIC_API_KEY from .env

def claude_vision_conversation(
    parsed_file_contents: dict, 
    base_path,
    config: dict | None = None,
    ) -> str:

    model_name, system_msg, model_options = get_config(config)

    client = anthropic.Anthropic()

    conversation = parsed_file_contents['conversation']
    rehydrated_conversation = add_image_data_to_conversation(conversation,base_path)

    # return rehydrated_conversation

    message = client.messages.create(
        model=model_name,
        system=system_msg,
        max_tokens=model_options.pop('max_tokens',4096),
        messages= rehydrated_conversation,
        **model_options
    )

    response = message.content[0].text
    formatted_response = "\n# %Assistant\n\n" + response
    return formatted_response