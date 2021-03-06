import argparse
import os
import sys
import traceback

import yaml

from migrant.migrate.migrate import Migrate


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


class UpgradeStateDBCommand(Command):
    """
    Upgrade schemas in storage to actual schema in models
    """
    command = 'upgrade'
    help_this_command = 'make new schema migration'

    def init_arg_parse(self):
        _parser = super().init_arg_parse()
        _parser.add_argument('--db',
                             action='store_true',
                             help='upload to storage not existed migrations from db(Not recommended use )')

        _parser.add_argument('--schema',
                             action='store_true',
                             help='get actual state schema and make migration file',
                             default=True)
        return _parser

    def execute(self):
        args = self.parser.parse_args()
        settings_file = args.settings \
            if '.yaml' in args.settings \
            else args.settings + '.yaml'
        migrate = Migrate(settings_file=settings_file)
        if args.db:
            raise NotImplementedError
        elif args.schema:
            migrate.upgrade()
        else:
            print(self.parser.format_help())


class DowngradeStateDBCommand(Command):
    """
    Downgrade schema to concrete schema
    """
    command = 'downgrade'
    help_this_command = 'command for downgrade state schema '

    def execute(self):
        args = self.parser.parse_args()
        settings_file = args.settings \
            if '.yaml' in args.settings \
            else args.settings + '.yaml'
        downgrade_to = args.downgrade_to
        migrate = Migrate(settings_file=settings_file)
        migrate.downgrade(downgrade_to_migration=downgrade_to)

    def init_arg_parse(self):
        _parser = super().init_arg_parse()
        _parser.add_argument('--downgrade_to',
                             help='name of migration to which the state of the database should be downgrade',
                             default=None)
        return _parser


class StatusMigrationsCommand(Command):
    """
    Get status migrations
    """
    command = 'status'
    help_this_command = 'get name last migration on files or in db'

    def init_arg_parse(self):
        _parser = super().init_arg_parse()
        _parser.add_argument('--db',
                             action='store_true',
                             help='get last migration in db')

        _parser.add_argument('--storage',
                             action='store_true',
                             help='get last migration in file storage')
        _parser.add_argument('--diff',
                             action='store_true',
                             help='get difference between last migration in storage and in db',
                             )
        return _parser

    def execute(self):
        args = self.parser.parse_args()
        settings_file = args.settings \
            if '.yaml' in args.settings \
            else args.settings + '.yaml'
        migrate = Migrate(settings_file=settings_file)
        print(args.db, args.storage, args.diff)
        if args.db:
            migrate.get_status('db')
        elif args.storage:
            migrate.get_status('storage')
        elif args.diff:
            migrate.get_status('diff')
        else:
            print(self.parser.format_help())


class MigrateToDbCommand(Command):
    """
    Implement migrations to not existed to db
    """
    command = 'migrate'
    help_this_command = 'Apply schemas not existed in db'

    def execute(self):
        args = self.parser.parse_args()
        settings_file = args.settings \
            if '.yaml' in args.settings \
            else args.settings + '.yaml'
        migrate = Migrate(settings_file=settings_file)
        try:
            migrate.upload()
        except ValueError:
            print('We could not change the database due to lack of connection to db')
            print("Please add/change 'engine_str' in your settings file")
        except:
            print('Unknown error')
            traceback.print_exc()


class CommandHandlerCommandLine:
    def __init__(self, argv, **kwargs):
        path_to_python = kwargs.get('path_to_python', 'python')
        path_to_folder = kwargs.get('path_to_folder', '')
        settings_file = 'migrate.yaml'
        if '--settings' in argv:
            settings_file = argv[argv.index('--settings') + 1]
        folder_migration = CommandHandlerCommandLine.get_folder_migration_from_settings(settings_file)
        path_to_folder = os.path.join(path_to_folder, folder_migration)
        command = ' '.join([path_to_python, path_to_folder, *argv[1:]])
        os.system(command)
        sys.exit(0)

    @staticmethod
    def get_folder_migration_from_settings(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = yaml.load(file)
        except:
            Migrate()
            with open(path, 'r', encoding='utf-8') as file:
                data = yaml.load(file)
        return data.get('name_folder_with_migrations', 'migrations')


class CommandsHandler:

    def __init__(self, argv, **kwargs):
        self.argv = argv
        if kwargs.get('is_run', False):
            CommandHandlerCommandLine(argv, **kwargs)
        self.__command_name = self.argv[1] if len(self.argv) > 1 else ''
        self.path_to_launcher = kwargs.get('path_to_launcher', '')
        self.__commands = dict()
        self.__init_commands()
        self.__process()

    def __init_commands(self):

        self.__commands = {
            'init': InitMigrationsCommand(self.argv, self.path_to_launcher),
            'upgrade': UpgradeStateDBCommand(self.argv, self.path_to_launcher),
            'downgrade': DowngradeStateDBCommand(self.argv, self.path_to_launcher),
            'status': StatusMigrationsCommand(self.argv, self.path_to_launcher),
            'migrate': MigrateToDbCommand(self.argv, self.path_to_launcher)
        }

    def __process(self):
        if self.__command_name in self.__commands:
            command = self.__commands[self.__command_name]
            command.execute()
        else:
            for command in self.__commands.values():
                print(command.__doc__)
