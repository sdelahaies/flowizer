from ollama import chat


def prompt(document=None):
    return """Extract the product\'s name and estimated carbon footprint from the document below:
<document>    
{document}
</document>
return the information as json object using the following keys:

'name': 'product_name',
'footprint': 'product_footprint'

Do not add any additional information to the output.
""".format(document = document)


def ollama_fn(input: dict, param={}):
    try:
        key = list(input.keys())[0]
        messages = []
        if "model" in param.keys():
            model = param["model"]
        if "system" in param.keys():
            system_prompt = param["system"]
            messages.append({"role": "system", "content": system_prompt})
            
        if "text" in input[key]:
            text = input[key]["text"]
            messages.append({"role": "user", "content": prompt(text)})
        response = chat(model=model, messages=messages,options={"temperature":0.})
        return {"text": response.message.content}
    except Exception as e:
        return {"error": str(e)}

