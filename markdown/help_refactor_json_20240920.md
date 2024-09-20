# %User

An API returns json as a key-value mapping with this format:

```json
{"Police officer - Lancashire Constabulary":
    {
        "1":{"id":"3312","description":"Police officers (sergeant and below)","distance":0.45},
        "2":{"id":"3314","description":"Prison service officers (below principal officer)","distance":0.61},
        "3":{"id":"1163","description":"Senior officers in fire, ambulance, prison and related services","distance":0.63},
        ...
    },
"Labourer - Barratt Homes":
    {
        "1":{"id":"8159","description":"Construction operatives n.e.c.","distance":0.65},
        "2":{"id":"9252","description":"Warehouse operatives","distance":0.71},
        "3":{"id":"8153","description":"Rail construction and maintenance operatives","distance":0.73},
        ...
    },
...
}
```

This is really annoying. The outer keys are strings sent to the API and the inner keys are just ascending numbers. There can be any number of strings sent to the API, and for each id, any number responses. I need to reformat like this:

```json
{
    [
        {
            "request":"Police officer - Lancashire Constabulary",
            "response":[
                {"id":"3312","description":"Police officers (sergeant and below)","distance":0.45},
                {"id":"3314","description":"Prison service officers (below principal officer)","distance":0.61},
                {"id":"1163","description":"Senior officers in fire, ambulance, prison and related services","distance":0.63},
                ...
            ]
         },
         {
            "request":"Labourer - Barratt Homes",
            "response":[
                {"id":"8159","description":"Construction operatives n.e.c.","distance":0.65},
                {"id":"9252","description":"Warehouse operatives","distance":0.71},
                {"id":"8153","description":"Rail construction and maintenance operatives","distance":0.73},
                ...
            ]
         },
         ...
    ]  
}
```

I'm doing this in a Flask backend. Can you give me the python code to reformat the json like this? 


# %Assistant

Certainly! Here's a Python function that you can use in your Flask backend to reformat the JSON as requested:

```python
def reformat_json(input_json):
    reformatted = []
    
    for request, responses in input_json.items():
        reformatted_item = {
            "request": request,
            "response": [value for key, value in sorted(responses.items(), key=lambda x: int(x[0]))]
        }
        reformatted.append(reformatted_item)
    
    return {"data": reformatted}

# Usage in your Flask route
from flask import jsonify

@app.route('/your-endpoint', methods=['POST'])
def your_endpoint():
    # Assuming you receive the JSON data in the request
    input_json = request.json
    
    # Reformat the JSON
    reformatted_json = reformat_json(input_json)
    
    # Return the reformatted JSON
    return jsonify(reformatted_json)
```

This function does the following:

1. It creates an empty list called `reformatted` to store the reformatted items.

2. It iterates through each key-value pair in the input JSON.

3. For each pair, it creates a new dictionary with two keys:
   - "request": The original key (e.g., "Police officer - Lancashire Constabulary")
   - "response": A list of all the response items, sorted by their numeric keys

4. The response items are sorted using the `sorted()` function with a key function that converts the string keys to integers, ensuring they're in the correct order.

5. Each reformatted item is appended to the `reformatted` list.

6. Finally, it returns a dictionary with a single key "data" containing the reformatted list.

In your Flask route, you can use this function to reformat the incoming JSON data and then return it using `jsonify()`.

This approach will work regardless of the number of requests or the number of responses for each request. It also maintains the order of the responses based on their numeric keys.

# %User

Great thanks. But the JSON I'm dealing with isn't from my app - it's from an API function, and the JSON is returned as a string. How do I convert into a format that I can feed into your function?

# %Assistant

Ah, I see. If the JSON is returned as a string from an API, you'll need to parse it first before passing it to the reformat function. Here's how you can modify the process:

```python
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

def reformat_json(input_json):
    reformatted = []
    
    for request, responses in input_json.items():
        reformatted_item = {
            "request": request,
            "response": [value for key, value in sorted(responses.items(), key=lambda x: int(x[0]))]
        }
        reformatted.append(reformatted_item)
    
    return {"data": reformatted}

@app.route('/your-endpoint', methods=['POST'])
def your_endpoint():
    # Assuming you receive the JSON string in the request body
    json_string = request.data.decode('utf-8')
    
    try:
        # Parse the JSON string into a Python dictionary
        input_json = json.loads(json_string)
        
        # Reformat the JSON
        reformatted_json = reformat_json(input_json)
        
        # Return the reformatted JSON
        return jsonify(reformatted_json)
    
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400

if __name__ == '__main__':
    app.run(debug=True)
```

Here's what's changed:

1. We import the `json` module at the top of the file.

2. In the Flask route, we first decode the request data from bytes to a UTF-8 string using `request.data.decode('utf-8')`.

3. We then use `json.loads()` to parse the JSON string into a Python dictionary. This function will raise a `json.JSONDecodeError` if the string is not valid JSON.

4. We wrap this in a try-except block to handle potential JSON parsing errors.

5. If parsing is successful, we proceed with reformatting and returning the JSON as before.

6. If there's a parsing error, we return an error message with a 400 status code.

This approach will allow you to handle JSON strings from external APIs, parse them into Python dictionaries, and then reformat them using the function we created earlier.

Remember to adjust the error handling and response format as needed for your specific application. Also, ensure that your Flask app has the necessary CORS settings if you're calling this endpoint from a different origin.