import os
from _model.schema import Schema
import sys
from _utils.settings import SettingsGlobal,SettingsMigrations
from _db_adaptation.db_util import DbUtil
from .migration import Migration


class Migrate:
    def __init__(self, db_connect=None,
                 settings_file='migrate.yaml'):
        if not isinstance(db_connect, DbUtil):
            raise TypeError('db_connect must be extand class DbUtil')
        self.db_connect = db_connect
        self.settings_file = settings_file
        self.settings = SettingsGlobal(settings_file)
        self.settings_migrations = SettingsMigrations(self.settings)
        self.schema = Schema(self.db_connect)
        self.path_to_migrations_folder = os.path.join(self.settings.name_folder_with_migrations,
                                                      'migrations')
        # self.init_migrate()

    def migrate(self):
        self.schema.make_current_state_schema()

    def init(self):
        """
        проверяет если нет миграций в файле и в базе то создает первую миграцию
        если есть то ничего не делает

        :return:
        """

        def is_existed_files_in_folder(path_to_migrations_folder):
            return len(os.listdir(path_to_migrations_folder)) > 0

        # print(path)
        if is_existed_files_in_folder(self.path_to_migrations_folder):
            print('Migations was inited')
        else:
            # TODO make got migrations from files
            print('start init migrations')
            migration = Migration(self.settings)
            schema_to_insert = self.schema.get_current_schema(with_objects=False)
            migration.init_migration(schema_to_insert)

            pass

    def upgrade(self):
        pass

    def downgrade(self):
        pass
