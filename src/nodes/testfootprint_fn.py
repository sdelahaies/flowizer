import json

def testfootprint_fn(input, param={}):
    try:
        key = list(input.keys())[0]
        data = json.loads(input[key]['text'])
        #print(data)
        if float(data["footprint"])>450:
            return {'branch': 'AcceptFootprint'}
        else:
            return {'branch': 'RejectFootprint'}
    except Exception as e:
        return {"error": str(e)}