from colorama import Fore, Style

def print_logo():
    logo = """
    ┌┬┐┬ ┬┬─┐┌─┐┬ ┬┬ ┬ ┐┌─┐  ┬  ┌─┐┬ ┬
    ││││ │├┬┘├─┘├─┤└┬┘  └─┐  │  ├─┤│││
    ┴ ┴└─┘┴└─┴  ┴ ┴ ┴   └─┘  ┴─┘┴ ┴└┴┘
    """
    print(Fore.BLUE + logo + Style.RESET_ALL)
