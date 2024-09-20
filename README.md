# Markdown Chat with LLM

![GitHub license](https://img.shields.io/github/license/matweldon/llm_tool)
![GitHub stars](https://img.shields.io/github/stars/matweldon/llm_tool)
![GitHub forks](https://img.shields.io/github/forks/matweldon/llm_tool)
![GitHub issues](https://img.shields.io/github/issues/matweldon/llm_tool)

Chat with an LLM directly in your markdown documents!

This command line tool extends Simon Willison's `llm` tool to allow you to have a conversation with an LLM in a markdown document. The idea is that you then have a permanent record of the conversation which you can submit to version control.

This project is work-in-progress and only really for myself. This README was mainly written by an LLM which is why it's so corny, and wrong.

## Features

- Seamless integration with markdown files
- Real-time responses from a powerful language model
- Easy-to-use interface
- Customizable prompts and settings

## Installation

1. Clone the repository:
   git clone https://github.com/matweldon/llm_tool.git

2. Navigate to the project directory:
   cd llm_tool

3. Install the required dependencies:
   pip install -r requirements.txt

4. Set up your API key:
   export LLM_API_KEY=your_api_key_here

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

> # %User
>
> \!\[image1\]\(data/cats.png\)
> How many cats are in the image? Are there any black cats?

and then run the command. So far, I've only tested this with png files but it should also work with JPEG.

## Configuration

You can customize the behavior of the chat by editing the `config.yml` file:

- `model`: Choose the LLM model to use
- `temperature`: Adjust the creativity of the responses
- `max_tokens`: Set the maximum length of the generated text

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Thanks to the creators of the LLM API for making this project possible
- Inspired by the growing trend of AI-assisted writing and coding
