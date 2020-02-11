import json

def get():
    with open('config/CONFIG.json','r') as f:
        data = json.load(f)
    return data

def set(data):
    with open('config/CONFIG.json','w') as f:
        json.dump(data,f)

def update(kwargs):
    data = get()
    data.update(kwargs)
    set(data)