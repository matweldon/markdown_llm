import llm
import os
import sys
import re
from llm_tool import OBSIDIAN_DIR

def parse_file_contents(file_contents):
    pattern = r'%%(\w+)%%(.*?)(?=%%|$)'
    matches = re.findall(pattern, file_contents, re.DOTALL)
    
    result = []
    for role, text in matches:
        result.append({
            "role": role.lower(),
            "text": text.strip()
        })
    
    return result



def text_llm(file_path: str | os.PathLike) -> None:
    """
    Read a file, parse as llm prompt, and append the result back to the original file.

    This function reads the contents of the file specified by `file_path`,
    parses it as an llm prompt, sends the prompt to the llm, and then appends the response
    back to the end of the original file. The original file contents are not overwritten.

    Parameters
    ----------
    file_path : str or os.PathLike
        The path to the file to be processed.

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    PermissionError
        If the user doesn't have permission to read or write the file.
    IOError
        If there's an error reading from or writing to the file.

    Examples
    --------
    >>> text_llm('/path/to/your/file.txt')
    """
    # Normalize the file path
    file_path = os.path.normpath(file_path)

    model = llm.get_model("sonnet")
    conversation = model.conversation()

    try:
        # Read the file contents
        with open(file_path, 'r') as file:
            content = file.read()

        parsed = parse_file_contents(content)

        prompts = [chunk['text'] for chunk in parsed if chunk['role']=='prompt']
        responses = [chunk['text'] for chunk in parsed if chunk['role']=='response']
        
        assert len(prompts)>=len(responses), "There are more responses than prompts. Why?"
        conversation.responses += [
            llm.Response.fake(prompt=prompt,
            response=response,
            model=model,
            system="") 
            for prompt, response in zip(prompts,responses)
        ]
        
        if len(prompts) == len(responses) + 1:
            new_response = conversation.prompt(prompts[-1]).text()
            new_formatted_response = f"\n%%response%%\n\n{new_response}"
            # Append the modified content back to the file
            with open(file_path, 'a') as file:
                file.write('\n' + new_formatted_response)
        else:
            print("No new prompts.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except PermissionError:
        print(f"Error: Permission denied when trying to access '{file_path}'.")
    except IOError as e:
        print(f"Error: An I/O error occurred: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        patharg = sys.argv[1]
        text_llm(patharg)
    else:
        print("No argument provided")