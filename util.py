def user_choice(choices: list[str]) -> int:
    for i, s in enumerate(choices):
        print(f"{i+1}) {s}")
    _c = input("Enter Choice >") or "1"
    return int(_c) - 1

def boolean_user_choice() -> bool:
    _c = input("Enter Choice (Y/n) >")
    if _c == "":
        return True
    return _c == "y" or _c == "Y" or _c == "yes" or _c == "Yes" or _c == "YES" or _c == "true" or _c == "True" or _c == "TRUE" or _c == "1"

class ANSI:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'