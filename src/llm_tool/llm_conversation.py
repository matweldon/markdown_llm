import llm

def chunk_user_assistant_turns(conversation):
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


def llm_conversation(parsed_file_contents):
    # assert parsed_file_contents['metadata']['has_images'] == False,(
    #     "llm can't handle conversations with images"
    # )

    chunked_conversation = chunk_user_assistant_turns(parsed_file_contents['conversation'])
    
    model = llm.get_model('claude-3-5-sonnet-20240620')
    conversation = model.conversation()

    if 'assistant' not in chunked_conversation[-1].keys():
        new_prompt = chunked_conversation.pop()
    
        conversation.responses += [
            llm.Response.fake(prompt=turn['user'],
            response=turn['assistant'],
            model=model,
            system="")
            for turn in chunked_conversation
        ]

        new_response = conversation.prompt(new_prompt['user'])
        new_formatted_response = f"\n# %Assistant\n\n{new_response}"
    else:
        print('No new prompts.')
        new_formatted_response = ''

    return new_formatted_response





