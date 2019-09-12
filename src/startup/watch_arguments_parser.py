import re
import argparse
import secrets


class Parser:
    """Class that handles all the arguments given by the user.

    Almost all the arguments have default values, the only one that is required is the conf.
    This argument is necessary because the project it is not intended to have any configuration files."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='Watch Replay')
        self.secret = secrets.token_urlsafe(15)
        self.add_arguments()

    def add_arguments(self):
        """Add all the arguments to the parser."""

        self.parser.add_argument('-match', required=True, type=str)
        self.parser.add_argument('-url', required=False, type=str, default='127.0.0.1')
        self.parser.add_argument('-port', required=False, type=int, default=8000)
        self.parser.add_argument('-pyv', required=False, type=str, default='')

    def get_arguments(self):
        """Return all the arguments.

        :returns list: List of arguments"""

        args = self.parser.parse_args()

        return [args.match, args.url, args.port], args.pyv
