from colorama import Fore, Back, Style, init

# 初始化 colorama
init(autoreset=True)

def print_red(message, bg=False):
    color = f"{Fore.RED}{Back.YELLOW}" if bg else Fore.RED
    print(f"{color}{message}{Style.RESET_ALL}")

def print_green(message, bg=False):
    color = f"{Fore.GREEN}{Back.YELLOW}" if bg else Fore.GREEN
    print(f"{color}{message}{Style.RESET_ALL}")

def print_blue(message, bg=False):
    color = f"{Fore.BLUE}{Back.YELLOW}" if bg else Fore.BLUE
    print(f"{color}{message}{Style.RESET_ALL}")

def print_white(message, bg=False):
    color = f"{Fore.WHITE}{Back.YELLOW}" if bg else Fore.WHITE
    print(f"{color}{message}{Style.RESET_ALL}")

def print_yellow(message, bg=False):
    color = f"{Fore.YELLOW}{Back.YELLOW}" if bg else Fore.YELLOW
    print(f"{color}{message}{Style.RESET_ALL}")

# 示例用法
if __name__ == "__main__":
    print_red("This is a red message")
    print_green("This is a green message")
    print_blue("This is a blue message")
    print_red("This is a red message with yellow background", bg=True)
    print_green("This is a green message with yellow background", bg=True)
    print_blue("This is a blue message with yellow background", bg=True)
    print_white("This is a white message with yellow background", bg=True)