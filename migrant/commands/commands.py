import argparse


class Command:
    @property
    def command(self):
        raise NotImplementedError

    @property
    def help_this_command(self):
        raise NotImplementedError

    def __init__(self, argv,
                 path_to_launcher):
        self.argv = argv
        self.path_to_launcher = path_to_launcher
        self.parser = self.init_arg_parse()

    def init_arg_parse(self):
        _parser = argparse.ArgumentParser('args init command')
        _parser.add_argument(self.command,
                             help=self.help_this_command)
        _parser.add_argument('--settings',
                             help='files with settings',
                             default='migrate.yaml')
        return _parser

    def execute(self):
        raise NotImplementedError


class InitMigrationsCommand(Command):
    """
    run 'init' for make migrations
    """
    command = 'init'
    help_this_command = 'command for init migrations'

    def execute(self):
        args = self.parser.parse_args()
        settings_file = args.settings \
            if '.yaml' in args.settings \
            else args.settings + '.yaml'


class CommandsHandler:

    def __init__(self, argv, **kwargs):
        self.argv = argv

        self.__command_name = self.argv[1] if len(self.argv) > 1 else ''
        self.path_to_launcher = kwargs.get('path_to_launcher', '')
        self.__commands = dict()
        self.__init_commands()
        self.__process()

    def __init_commands(self):

        self.__commands = {
            'init': InitMigrationsCommand(self.argv, self.path_to_launcher),
        }

    def __process(self):
        if self.__command_name in self.__commands:
            command = self.__commands[self.__command_name]
            command.execute()
        else:
            for command in self.__commands.values():
                print(command.__doc__)
