import json

def jsonload(file):
    with open(file) as f:
        return json.load(f)

def jsonsave(file, data):
    with open(file, 'w') as f:
        jdata = str(data)
        jdata = jdata.replace("'", '"')
        jload = json.loads(jdata)
        jdump = json.dumps(jload, sort_keys=True, indent=4)
        f.write(str(jdump))