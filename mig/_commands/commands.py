from _migrate.migrate import Migrate

import sys
import argparse

sys.path.append("..")


class Command:
    def __init__(self, argv,
                 path_to_launcher):
        self.argv = argv
        self.path_to_launcher = path_to_launcher
        self.parser = self.init_arg_parse()

    def init_arg_parse(self):
        # _parser = argparse.ArgumentParser('')
        # return _parser
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError


class InitMigrationsCommand(Command):
    """
    run 'init' for make migrations
    """
    def init_arg_parse(self):
        _parser = argparse.ArgumentParser('args init command')
        _parser.add_argument('init',
                             help='command for init migrations')
        _parser.add_argument('--settings',
                             help='files with settings',
                             default='migrate.yaml')
        return _parser

    def execute(self):
        args = self.parser.parse_args()
        settings_file = args.settings \
            if '.yaml' in args.settings \
            else args.settings + '.yaml'
        Migrate(settings_file=settings_file)
        # mi.init_migrate(self.path_to_launcher, args.folder)


class UpdateStateDBCommand(Command):
    def execute(self):
        pass

    def init_arg_parse(self):
        pass

class CommandsHandler:

    def __init__(self, argv, **kwargs):
        self.argv = argv

        self.command_name = self.argv[1] if len(self.argv) > 1 else ''
        self.path_to_launcher = kwargs.get('path_to_launcher', '')
        self.init_commands()

    def init_commands(self):
        self.commands = dict()
        self.commands = {
            'init': InitMigrationsCommand(self.argv, self.path_to_launcher),
            'update': UpdateStateDBCommand(self.argv, self.path_to_launcher)

        }

    def process(self):
        if self.command_name in self.commands:
            command = self.commands[self.command_name]
            command.execute()
        else:
            for command in self.commands.values():
                print(command.__doc__)
            print('The list of available strategies to scan LB below:')
