# Markdown Chat with LLM

![GitHub license](https://img.shields.io/github/license/matweldon/llm_tool)
![GitHub stars](https://img.shields.io/github/stars/matweldon/llm_tool)
![GitHub forks](https://img.shields.io/github/forks/matweldon/llm_tool)
![GitHub issues](https://img.shields.io/github/issues/matweldon/llm_tool)

Chat with an LLM directly in your markdown documents!

This command line tool extends Simon Willison's amazing [llm](https://github.com/simonw/llm) tool to allow you to have a conversation with an LLM in a markdown document. The idea is that you then have a permanent record of the conversation which you can submit to version control or keep in your [Obsidian](https://obsidian.md) vault.

Why would you want to use this instead of `llm chat`?

* It's easier to save conversations to version control and/or Obsidian
* Text editing and navigation are limited in the terminal
* Working in a markdown document, you get nice syntax highlighting when the LLM writes fenced code blocks
* You can comment out parts of the conversation history and rerun them (see below)
* This tool has support for markdown links to images. Hyperlinks to other documents and websites to follow.

This project is a very early work-in-progress. Use only if you're willing to troubleshoot.

## Installation

1. Clone the repository:

```bash   
git clone https://github.com/matweldon/llm_tool.git
```

2. Navigate to the project directory:

```bash
cd llm_tool
```

3. Install as a package

```bash
pip install .
```

4. Set the API key (see below).


## API key management

The `llm` package provides key management which can be used in this package for text models. To set the Anthropic key, enter:

```bash
llm keys set claude
```
and enter the key at the prompt. The package stores keys in a JSON file at a location that can be found with `llm keys path`.

The vision model will work with an 'ANTHROPIC_API_KEY' in a `.env` file in the root of the directory where the package is used, or by setting the environment variable in the session. In the future the package will support other models but the Anthropic model is currently hard-coded.

## Usage

Open your markdown file, and add the following syntax where you want to start a chat:

```
# %User

Write the prompt here...
```

Run the script:
   
   `python -m llm_tool your_file.md`

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

The API is stateless - the API call reconstructs the full conversation each time a request is sent. This means that you can "put words into the LLM's mouth" and generally mess around with the flow of the conversation. Although LLMs are pretty wise to this, and in my experience will tell you off if you try to make them think they've said outrageous things.

### Models

Currently, Anthropic Claude Sonnet 3.5 is hard-coded. But using the Python SDK of the `llm` package means that in principle this supports any models Simon Willison's package does.

### Configuration

You can optionally set model, system message and other options for the conversation with a YAML header at the top of the markdown document.

When using text-only (not vision) models, you can specify the model using aliases set with `llm aliases set` from the llm package.

```
---
model: sonnet # This is an alias 
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


### Images

The tool supports vision models - currently only Anthropic. To add an image to the chat, add a markdown link to the relative path of the image:

```
# %User

![image1](data/cats.png)
How many cats are in the image? Are there any black cats?
```

and then run the command. So far, I've only tested this with png files but it should also work with JPEG.

Image markdown supports the same options, but aliases are not supported because the package calls the Anthropic API directly rather than using `llm`.

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
