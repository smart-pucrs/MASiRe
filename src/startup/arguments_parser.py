import re
import argparse
import secrets


class Parser:
    """Class that handles all the arguments given by the user.

    Almost all the arguments have default values, the only one that is required is the conf.
    This argument is necessary because the project it is not intended to have any configuration files."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='Disaster Simulator')
        self.secret = secrets.token_urlsafe(15)
        self.add_arguments()

    def add_arguments(self):
        """Add all the arguments to the parser."""

        self.parser.add_argument('-conf', required=True, type=str)
        self.parser.add_argument('-url', required=False, type=str, default='127.0.0.1')
        self.parser.add_argument('-sp', required=False, type=str, default='8910')
        self.parser.add_argument('-ap', required=False, type=str, default='12345')
        self.parser.add_argument('-pyv', required=False, type=str, default='')
        self.parser.add_argument('-g', required=False, type=bool, default=False)
        self.parser.add_argument('-step_t', required=False, type=int, default=30)
        self.parser.add_argument('-first_t', required=False, type=int, default=60)
        self.parser.add_argument('-mtd', required=False, type=str, default='time')
        self.parser.add_argument('-log', required=False, type=str, default='true')
        self.parser.add_argument('-secret', required=False, type=str, default='')

    def check_arguments(self):
        """Check all the arguments to prevent wrong format.

        :returns int: Status of error, if any found than return 0 else 1
        :returns str: Message of the error so the user can fix it."""

        args = self.parser.parse_args().__dict__

        if args['url'].startswith('http'):
            return 0, 'URL can not have the "http://" prefix.'

        if re.findall('//', args['url']):
            return 0, 'URL can not have the "//" prefix.'

        if args['url'] != 'localhost' and re.findall('[a-zA-Z]+', args['url']) and not re.findall('[a-zA-Z_-]+?\.[a-zA-Z]{2,4}', args['url']):
            return 0, 'Invalid URL. If URL is not localhost, than it must have at least ".com" after the name.'

        if re.findall('\D', args['sp']):
            return 0, 'Simulation port must be made of numbers only.'

        if int(args['sp']) < 1024:
            return 0, 'Simulation port can not be under 1024 (system only).'

        if int(args['sp']) > 65535:
            return 0, 'Simulation port invalid.'

        if re.findall('\D', args['ap']):
            return 0, 'API port must be made of numbers only.'

        if int(args['ap']) < 1024:
            return 0, 'API port can not be under 1024 (system only).'

        if int(args['ap']) > 65535:
            return 0, 'API port invalid.'

        if re.findall('\d', args['pyv']) and int(args['pyv']) != 3:
            return 0, 'Invalid python version. The system accepts either "" or "3".'

        if str(args['g']).lower() != 'true' and str(args['g']).lower() != 'false':
            return 0, f'Invalid value for globally argument: "{args["g"]}".'

        if re.findall('\D', str(args['step_t'])):
            return 0, 'Step time argument must receive only integers.'

        if int(args['step_t']) <= 1:
            return 0, 'Step time must be bigger than 1 to prevent execution time errors. ' \
                      'Note that bigger numbers does not represent that the simulation will ' \
                      'take longer to finish as long as the agents keep interacting with it.'

        if re.findall('\D', str(args['first_t'])):
            return 0, 'First step time argument must receive only integers.'

        if int(args['first_t']) <= 1:
            return 0, 'First step time must be bigger than 1 to prevent execution time errors. ' \
                      'Note that bigger numbers does not represent that the simulation will ' \
                      'take longer to start as long as the agents connect to it.'

        if args['mtd'] != 'time' and args['mtd'] != 'button':
            return 0, f'Invalid option given to method argument: "{args["mtd"]}".'

        if str(args['log']).lower() != 'true' and str(args['log']).lower() != 'false':
            return 0, f'Invalid value for log argument: "{args["log"]}".'

        return 1, 'Arguments ok.'

    def get_argument(self, arg):
        """Return the argument requested.

        :param arg: Argument requested
        :returns [None|primitive type obj]: None if argument not find else the value hold on the variable."""

        args = self.parser.parse_args()
        for argument in args.__dict__:
            if argument == arg:
                if argument == 'url' and args[argument] == 'localhost':
                    return '127.0.0.1'
                else:
                    return args.__dict__[arg]

        return None

    def get_simulation_arguments(self):
        """Return all the arguments necessary for the Simulation.

        :returns list: List of arguments"""

        args = self.parser.parse_args()

        if not args.secret:
            secret = self.secret
        else:
            secret = args.secret

        if args.url == 'localhost':
            args.url = '127.0.0.1'

        return [args.conf, args.url, args.sp, args.ap, args.log, secret]

    def get_api_arguments(self):
        """Return all the arguments necessary for the API.

        :returns list: List of arguments"""

        args = self.parser.parse_args()

        if not args.secret:
            secret = self.secret
        else:
            secret = args.secret

        if args.url == 'localhost':
            args.url = '127.0.0.1'

        return [args.url, args.ap, args.sp, args.step_t, args.first_t, args.mtd, secret]

    def get_arguments(self):
        """Return all the arguments.

        :returns list: List of arguments"""

        args = self.parser.parse_args()

        if args.url == 'localhost':
            args.url = '127.0.0.1'

        return [args.conf, args.url, args.sp, args.ap, args.pyv, args.g,
                args.step_t, args.first_t, args.mtd, args.secret]
