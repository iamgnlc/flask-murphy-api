from colorama import Fore, Style

LOGO = """
┌┬┐┬ ┬┬─┐┌─┐┬ ┬┬ ┬ ┐┌─┐  ┬  ┌─┐┬ ┬
││││ │├┬┘├─┘├─┤└┬┘  └─┐  │  ├─┤│││
┴ ┴└─┘┴└─┴  ┴ ┴ ┴   └─┘  ┴─┘┴ ┴└┴┘
"""

def print_logo():
    print(Fore.BLUE + LOGO + Style.RESET_ALL)
