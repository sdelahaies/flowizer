from ollama import chat


def ollama_fn_2(input: dict, param={}):
    try:
        #print(input)
        messages = []
        if "model" in param.keys():
            model = param["model"]
        if "system" in param.keys():
            system_prompt = param["system"]
            messages.append({"role": "system", "content": system_prompt})
    
        prompt = input["Prompt"]["text"]
        document = input["PDF2Text"]["text"]
        messages.append({"role": "user", "content": prompt.format(document=document)})
        response = chat(model=model, messages=messages,options={"temperature":0.})
        return {"text": response.message.content}
    except Exception as e:
        return {"error": str(e)}

