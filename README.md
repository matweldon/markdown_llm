# Markdown Chat with LLM

![GitHub license](https://img.shields.io/github/license/matweldon/llm_tool)
![GitHub stars](https://img.shields.io/github/stars/matweldon/llm_tool)
![GitHub forks](https://img.shields.io/github/forks/matweldon/llm_tool)
![GitHub issues](https://img.shields.io/github/issues/matweldon/llm_tool)

Chat with an LLM directly in your markdown documents!

This command line tool extends Simon Willison's amazing [llm](https://github.com/simonw/llm) tool to allow you to have a conversation with an LLM in a markdown document. The idea is that you then have a permanent record of the conversation which you can submit to version control or keep in your [Obsidian](https://obsidian.md) vault.

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

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

or install as a package using `pyproject.toml`

```bash
pip install .
```

or you should be able to just install from git but I haven't tried it.

4. Get an Anthropic API key and follow the instructions on Simon Willison's GitHub page to set it up. I think you probably also need to set up an alias called 'sonnet' for the package to work. No apologies - I told you this is work-in-progress.

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

You can also comment out parts of the conversation using `<!--llm` and `llm-->`. This allows you to edit the conversation history, for example to rerun responses to obtain a sample of several different answers.

The API is stateless - the API call reconstructs the full conversation each time a request is sent. This means that you can "put words into the LLM's mouth" and generally mess around with the flow of the conversation. Although LLMs are pretty wise to this, and in my experience will tell you off if you try to make them think they've said outrageous things.

### Models

Currently, Anthropic Claude Sonnet 3.5 is hard-coded (referred to by an alias, 'sonnet'). But using the Python SDK of the `llm` package means that in principle this supports any models Simon Willison's package does.

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

- Thanks to Simon Willison for creating the package this package depends on
- Thanks to the creators of the LLM APIs, especially Anthropic, for making this project possible
- Thanks to the creators of Obsidian for making me such a markdown addict
- Inspired by the growing trend of AI-assisted writing and coding
