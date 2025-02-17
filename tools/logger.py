from colorama import Fore

def log(log_type: str, message: str) -> None:
    if not isinstance(log_type, str) or not isinstance(message, str):
        raise TypeError(f"Arguments 'log_type' and 'message' must be strings. ''{type(log_type).__name__}' and '{type(message).__name__}' given.")

    match log_type:
        case "info":
            print(f"[{Fore.BLUE}INFO{Fore.RESET}]: {message}")
        case "warning":
            print(f"[{Fore.YELLOW}WARNING{Fore.RESET}]: {message}")
        case "error":
            print(f"[{Fore.RED}ERROR{Fore.RESET}]: {message}")
        case "success":
            print(f"[{Fore.GREEN}SUCCESS{Fore.RESET}]: {message}")
        case _:
            raise TypeError(f"Unknown log type: '{log_type}'")
