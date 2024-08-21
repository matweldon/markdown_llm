I have a python data structure representing a conversation between a user and an llm that looks like this:

```python
[{'role': 'user',
  'content': [{'type': 'text', 'text': 'How many cats are in this image?'},
   {'type': 'image', 'source': 'data/cats.png'},
   {'type': 'text', 'text': 'Are there any black cats?'}]},
 {'role': 'assistant',
  'content': 'There are 3 cats in both images.\n\nNo, there do not appear to be any black cats in either image'},
 {'role': 'user',
  'content': [{'type': 'text',
    'text': 'Thanks, new question: what is the first name of President Biden? Just give me the answer.'}]}]
```

I need a function to pair up subsequent user-assistant 'turns' and collapse it into a structure like this:

```python
[{'user': 'How many cats are in this image?\n\ndata/cats.png\n\nAre there any black cats?','assistant': 'There are 3 cats in both images.\n\nNo, there do not appear to be any black cats in either image'},
 {'user': 'Thanks, new question: what is the first name of President Biden? Just give me the answer.'}]
```

Notice that this is a list with two elements, where each element is a dictionary containing a user/assistant pair. Notice also that the multi-modal content for the user is ignored and is just collapsed into a single text string separated by newlines.