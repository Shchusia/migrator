from _migrate.migrate import Migrate

import sys
import argparse

sys.path.append("..")


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
        Migrate(settings_file=settings_file)
        # mi.init_migrate(self.path_to_launcher, args.folder)


class UpgradeStateDBCommand(Command):
    """

    """
    command = 'upgrade'
    help_this_command = ''

    def execute(self):
        args = self.parser.parse_args()
        settings_file = args.settings \
            if '.yaml' in args.settings \
            else args.settings + '.yaml'
        migrate = Migrate(settings_file=settings_file)
        migrate.upgrade()


class DowngradeStateDBCommand(Command):
    """

    """
    command = 'downgrade'
    help_this_command = 'command for downgrade state db'

    def execute(self):
        args = self.parser.parse_args()
        settings_file = args.settings \
            if '.yaml' in args.settings \
            else args.settings + '.yaml'
        downgrade_to = args.downgrade_to
        print(downgrade_to)
        migrate = Migrate(settings_file=settings_file)
        migrate.downgrade(downgrade_to_migration=downgrade_to)

    def init_arg_parse(self):
        _parser = super().init_arg_parse()
        _parser.add_argument('--downgrade_to',
                             help='name of migration to which the state of the database should be downgrade',
                             default=None)
        return _parser


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
            'upgrade': UpgradeStateDBCommand(self.argv, self.path_to_launcher),
            'downgrade': DowngradeStateDBCommand(self.argv, self.path_to_launcher),

        }

    def process(self):
        if self.command_name in self.commands:
            command = self.commands[self.command_name]
            command.execute()
        else:
            for command in self.commands.values():
                print(command.__doc__)
            print('The list of available strategies to scan LB below:')
