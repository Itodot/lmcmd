import argparse
from .terminal.terminal import CustomTerminal
initial_locals={}
def main():
    """
    The main function for the lmcmd command-line client.

    This function sets up an argument parser to accept a database name as a command-line argument.
    If a database name is provided, it initializes the `initial_locals` dictionary with the database name
    and starts an interactive terminal session using `CustomTerminal`.

    Arguments:
    None

    Returns:
    None
    """
    parser = argparse.ArgumentParser(description="lmcmd-The Fast lmdb Command Client")
    parser.add_argument("db", type=str, help="database name")
    args = parser.parse_args()

    if args.db:
        initial_locals['database']=args.db
        terminal=CustomTerminal(locals=initial_locals)
        terminal.interact()
if __name__ == "__main__":
    main()
