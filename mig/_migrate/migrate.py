import os
from _model.schema import Schema
import sys
from _utils.settings import SettingsGlobal,\
    SettingsMigrations
from _db_adaptation.db_util import DbUtil
from .migration import Migration, MigrationDb


class Migrate:
    def __init__(self,
                 db_connect=None,
                 settings_file='migrate.yaml'):
        if not isinstance(db_connect, DbUtil):
            raise TypeError('db_connect must be extand class DbUtil')
        self.db_connect = db_connect
        self.settings_file = settings_file
        self.settings = SettingsGlobal(settings_file)
        self.settings_migrations = SettingsMigrations(self.settings)
        self.schema = Schema(self.db_connect,
                             self.settings_migrations)
        self.path_to_migrations_folder = os.path.join(self.settings.name_folder_with_migrations,
                                                      'migrations')
        # self.init_migrate()

    # def migrate(self):
    #     self.schema.make_current_state_schema()

    def init(self):
        def is_existed_files_in_folder(path_to_migrations_folder):
            return len(os.listdir(path_to_migrations_folder)) > 0

        # print(path)
        if is_existed_files_in_folder(self.path_to_migrations_folder):
            print('Migrations exist')
            print('Please use command commit')
        else:
            # TODO make got migrations from files
            print('start init migrations')
            migration = Migration(self.settings)
            schema_to_insert = self.schema.get_current_schema(with_objects=False)
            migration.first_migration(schema_to_insert)

            pass

    def commit(self):
            # self.schema.get_migrations_schema()
        self.schema.get_migration_difference_previous_and_current_state()

    def upgrade(self):
        self.schema.make_tables()
        migration = self.schema.get_migration_difference_previous_and_current_state()
        if migration.empty():
            print('Any data to migrate')
        else:
            migration.save_migration()

    def upload(self):
        migration_db = MigrationDb(
            self.db_connect,
            self.settings_migrations)
        migration_db.make_transactions()


    def downgrade(self):
        pass
