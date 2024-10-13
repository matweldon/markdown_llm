# Markdown Chat with LLM

![GitHub license](https://img.shields.io/github/license/matweldon/llm_tool)
![GitHub stars](https://img.shields.io/github/stars/matweldon/llm_tool)
![GitHub forks](https://img.shields.io/github/forks/matweldon/llm_tool)
![GitHub issues](https://img.shields.io/github/issues/matweldon/llm_tool)

Chat with an LLM directly in your markdown documents!

This command line tool extends Simon Willison's amazing [llm](https://github.com/simonw/llm) tool to allow you to have a conversation with an LLM in a markdown document. The idea is that you then have a permanent record of the conversation which you can submit to version control or keep in your [Obsidian](https://obsidian.md) vault.

Why would you want to use this instead of `llm chat`?

* It's easier to save conversations to version control and/or Obsidian
* Using your favourite text editor is easier than the terminal
* Working in a markdown document, you get nice syntax highlighting when the LLM writes fenced code blocks
* You can comment out parts of the conversation history (see below)
* This tool has support for markdown links to images. Hyperlinks to other documents and websites to follow.
* It opens up possibilities for experimentation - by editing the chat history you can see how different models with different settings would answer the same question, and even get models conversing with each other.

This project is a very early work-in-progress. Use only if you're willing to troubleshoot.

## Installation

1. Install from git:

```bash
pip install git+https://github.com/matweldon/markdown_llm.git
```

OR, clone and install as editable for development:

```bash   
git clone https://github.com/matweldon/markdown_llm.git
cd markdown_llm
pip install -e .
```

2. Set the API key (see below).

3. (Optional) ensure you have the `code` command in your PATH, or edit the `EDITOR` option in `__init__.py` to open the text editor of your choice.


## API key management

Simon Willison's `llm` package provides key management which can be used in this package for text models. To set the Anthropic key, enter:

```bash
llm keys set claude
```
and enter the key at the prompt. The package stores keys in a JSON file at a location that can be found with `llm keys path`.

The vision model will work with an 'ANTHROPIC_API_KEY' in a `.env` file in the root of the directory where the package is used, or by setting the environment variable in the session. In the future the package will support other APIs but the Anthropic API is currently hard-coded for vision models.

## Usage

Open your markdown file, and add the following syntax where you want to start a chat:

```
# %User

Write the prompt here...
```

Run the script:
  
```bash
llmd your_file.md
```

The LLM's response will be inserted directly into your markdown file.

```
# %User
What is President Reagan's first name? Just give me the answer.

# %Assistant
Ronald
```

Then you can carry on the conversation

```
# %User
What about Thatcher?

# %Assistant
Margaret
```

You can also comment out parts of the conversation using `<!--llm` and `llm-->`. This allows you to edit the conversation history, for example to rerun responses to obtain a sample of several different answers.

The API is stateless - the API call reconstructs the full conversation each time a request is sent. This means that you can "put words into the LLM's mouth" and generally mess around with the flow of the conversation.

### Text editor integration

You don't have to start with an open text editor. You can create a new file with `llmd new_file.md` and start typing the prompt. Then run the command again to get the response. You just need to ensure the `code` command (for VS Code) is in your PATH. Or you can change the default 'open editor' command in `__init__.py` to work with other editors.

Once you've written a prompt, setting up a keyboard shortcut in your editor saves time moving back and forth between the editor and the terminal. To set up a keyboard shortcut in VS Code, open `keybindings.json` from the Command palette and add this entry (substituting your preferred key combination):

```json
    {
        "key": "cmd+ctrl+r",
        "command":"workbench.action.terminal.sendSequence",
        "args": {
            "text": "llmd ${file}\n"
        },
        "when": "editorTextFocus && editorLangId == markdown",
    }
```


### Models

Currently, the package has only been tested with Anthropic Claude Sonnet 3.5. But using the Python SDK of the `llm` package means that in principle this supports any models Simon Willison's package does. This includes OpenAI models and local open-source models. However, vision model use only supports Anthropic models.

There are some usage examples in the [examples](examples/) folder. You'll see that I used this package quite heavily in writing the package.

### Images

The tool supports vision models - currently only Anthropic. To add an image to the chat, add a markdown link to the relative path of the image:

```
# %User

![image1](data/cats.png)
How many cats are in the image? Are there any black cats?
```

and then run the command. So far, I've only tested this with png files but it should also work with JPEG.

Image markdown supports the same options, but aliases are not supported because the package calls the Anthropic API directly rather than using `llm`.


## Configuration

You can optionally set model, system message and other options for the conversation with a YAML header at the top of the markdown document.

When using text-only (not vision) models, you can specify the model using aliases set with `llm aliases set` from the llm package.

```
---
model: sonnet 
system: Only speak in French.
options:
  max_tokens: 1024
  temperature: 0.0
---

# %User
What is the capital of France?
```

Model options depend on the model type. For both OpenAI and Anthropic they include `temperature` and `max_tokens`. The options exposed through the llm package aren't very well documented so it's easiest to just look at the source code:

[Claude model options](https://github.com/simonw/llm-claude-3/blob/18d562a730643753ee0d65c7220deac2e9cde689/llm_claude_3.py#L18)

[OpenAI model options](https://github.com/simonw/llm/blob/d654c9521235a737e59a4f1d77cf4682589123ec/llm/default_plugins/openai_models.py#L163)

### System message templates and snippets

The package has a templated system message capability. All config is currently stored in the `__init__.py` file until I implement something better.

System messages can be added to the YAML header. They can make use of reusable snippets from the `CONFIG` dictionary. Any entry in the CONFIG dictionary with a prefix of `sys_` is a system message snippet and is available to be used in templated system messages.

For example, I have added a bulleted list of python preferences to the CONFIG dictionary as `sys_python_prefs`. This can then be used in the YAML header by adding a templated system message (see [templated_system_msg.md](examples/templated_system_msg.md)).


## To do

* Tidy up and improve config setting.
* Parse hyperlinks to other text files and inline the text, so that I don't have to copy and paste it all into the prompt
* Make it easier to install without having to use Simon W's API interface
* Parse links to websites, strip tags and inline the text

## Acknowledgments

- Thanks to Simon Willison for creating the package this package depends on
- Thanks to the creators of the LLM APIs, especially Anthropic, for making this project possible
- Thanks to the creators of Obsidian for making me such a markdown addict
- Inspired by the growing trend of AI-assisted writing and coding

# Notes

To test that the package works without the `llm` key management utilities, run `mv "$(llm keys path)" "$(llm keys path).bak"` and then try to run the package. Remember to change it back again after.
