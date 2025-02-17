import os
from exceptions import ParseError

def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except Exception:
        return False

def custom_split(string: str, separator: str, groupers: list[str] = ["'", '"']) -> list:
    if not isinstance(string, str) or not string:
        raise TypeError(f"Argument 'string' must be a non-empty string. '{type(string).__name__}' given.")
    if not isinstance(separator, str) or not separator:
        raise TypeError(f"Argument 'separator' must be a non-empty string. '{type(separator).__name__}' given.")

    result = [""]
    ignoring = False
    for char in string:
        if char in groupers:
            ignoring = not ignoring
        else:
            if char == separator and not ignoring:
                result.append("")
            else:
                result[-1] += char
    return result

def parse(string: str) -> dict:
    if not isinstance(string, str) or not string:
        raise TypeError(f"Argument 'string' must be a non-empty string. '{type(string).__name__}' given.")

    lines = string.split("\n")
    env = {}
    for line in lines:
        if line and not line.startswith("#"):
            if "=" not in line:
                raise ParseError(f"Invalid line: {line}")
            
            if "#" in line:
                line = line.split("#")[0]

            if '[' in line and ']' in line:
                values = line.split("[")[1].split("]")[0].split(",")
                key = line.split("=")[0]
                env[key] = values

                for value in env[key]: # Convert int values
                    if '"' not in value and is_int(value):
                        env[key][env[key].index(value)] = int(value)
            else:
                try:
                    key, value = custom_split(line, "=")
                    if value == "True":
                        value = True
                    elif value == "False":
                        value = False
                    
                    env[key] = value
                except Exception as e:
                    raise ParseError(e.__str__())
    return env

def load() -> dict:
    PATH = ".env.local" if os.path.exists(".env.local") else ".env"
    with open(PATH, "r") as f:
        file_content = f.read()
    return parse(file_content)

def get(key: str) -> str:
    env = load()
    return env[key]
