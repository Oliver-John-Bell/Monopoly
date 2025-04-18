from json_loader import load_json

def load_config():
    return load_json("config.json")

def load_spaces():
    return load_json("spaces.json")