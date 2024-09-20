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

1. Open your markdown file in your favorite text editor.
2. Add the following syntax where you want to start a chat:
> # %User
>
> Write the prompt here...

3. Run the script:
   python -m llm_tool path/to/your_file.md

4. The LLM's response will be inserted directly into your markdown file.

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
