# Markdown Chat with LLM

![GitHub license](https://img.shields.io/github/license/matweldon/llm_tool)
![GitHub stars](https://img.shields.io/github/stars/matweldon/llm_tool)
![GitHub forks](https://img.shields.io/github/forks/matweldon/llm_tool)
![GitHub issues](https://img.shields.io/github/issues/matweldon/llm_tool)

Chat with an LLM directly in your markdown documents!

This command line tool extends Simon Willison's amazing [llm](https://github.com/simonw/llm) tool to allow you to have a conversation with an LLM in a markdown document. The idea is that you then have a permanent record of the conversation which you can submit to version control.

This project is work-in-progress and only really for myself. This README was mainly written by an LLM which is why it's so corny, and wrong.

## Features

- Seamless integration with markdown files
- Real-time responses from a powerful language model
- Easy-to-use interface
- Customizable prompts and settings

## Installation

1. Clone the repository:
```bash   
git clone https://github.com/matweldon/llm_tool.git
```

2. Navigate to the project directory:

```bash
cd llm_tool
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```
or, using `pyproject.toml`

```bash
pip install .
```

4. Get an Anthropic API key and follow the instructions on Simon Willison's GitHub page to set it up.

## Usage

Open your markdown file, and add the following syntax where you want to start a chat:

> \# %User
>
> Write the prompt here...

Run the script:
   
   `python -m llm_tool your_file.md`

The LLM's response will be inserted directly into your markdown file.

> \# %User
> 
> What is President Reagan's first name? Just give me the answer.
>
> \# %Assistant
>
> Ronald

Then you can carry on the conversation

> \# %User
> 
> What about Thatcher?
>
> \# %Assistant
>
> Margaret

You can also comment out parts of the conversation using `<!--llm` and `llm-->`. This means that you can rerun responses to obtain different answers.

The API is stateless -- this means that the API call reconstructs the full conversation each time a request is sent. This means that you can "put words into the LLM's mouth" and generally mess around with the flow of the conversation.

### Images

The tool supports vision models -- currently only Anthropic Claude Sonnet 3.5.

To add an image to the chat, add a markdown link to the relative path of the image:

> \# %User
>
> \!\[image1\]\(data/cats.png\)
>
> How many cats are in the image? Are there any black cats?

and then run the command. So far, I've only tested this with png files but it should also work with JPEG.

## To do

* Add configuration options to change the model, system prompt, temperature etc
  - YAML header in markdown (I think this will be most useful)
  - config.toml
  - command line options
* Parse hyperlinks to other text files and inline the text, so that I don't have to copy and paste it all into the prompt
* Make it easier to deploy the package in other projects
* Make it easier to install without having to use Simon W's API interface
* Parse links to websites, strip tags and inline the text

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Thanks to the creators of the LLM API for making this project possible
- Inspired by the growing trend of AI-assisted writing and coding
