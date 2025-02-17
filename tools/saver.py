import os
import json
from tools.env_link import get
from tools.logger import log

def save(data: dict) -> None:
    PATH = get("SAVE_PATH")
    if not os.path.exists(PATH):
        log("warning", f"File not found: '{PATH}'")
        log("info", f"Creating save file at '{PATH}'")

    with open(PATH, "w") as f:
        json.dump(data, f, indent=4)

    log("success", f"Data saved to '{PATH}'")

def load() -> dict:
    PATH = get("SAVE_PATH")
    if not os.path.exists(PATH):
        log("warning", f"File not found: '{PATH}'")
        log("info", "Returning default data")
        data = {
            "repos": []
        }
    
    else:
        with open(PATH, "r") as f:
            data = json.load(f)
        log("success", f"Data loaded from '{PATH}'")
    
    return data

def update(data: dict) -> None:
    loaded_data = load()
    loaded_data.update(data)
    save(loaded_data)

    log("success", "Data updated")
