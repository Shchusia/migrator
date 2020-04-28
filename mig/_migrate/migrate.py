import os
from _model.schema import Schema
import sys
from _utils.settings import SettingsGlobal,\
    SettingsMigrations
from _db_adaptation.db_util import DbUtil
from .migration import Migration, MigrationDb, Migrations
from _connect.connect import Connect


class Migrate:
    def __init__(self,
                 db_connect=None,
                 settings_file='migrate.yaml'):
        self.settings_file = settings_file
        self.settings = SettingsGlobal(settings_file)
        self.settings_migrations = SettingsMigrations(self.settings)
        if db_connect is not None:
            if isinstance(db_connect, Connect):
                self.db_connect = db_connect.get_instance()
            elif isinstance(db_connect, DbUtil):
                self.db_connect = db_connect
            else:
                raise TypeError('db_connect must be extand class DbUtil')
        if db_connect is None and hasattr(self.settings, 'last_engine_str'):
            db_connect = Connect(getattr(self.settings, 'last_engine_str'))
            self.db_connect = db_connect.get_instance()
        else:
            self.settings.last_engine_str = self.db_connect.make_str_connect_engine()
        self.db_connect = db_connect

        self.schema = Schema(self.db_connect,
                             self.settings_migrations)
        self.path_to_migrations_folder = os.path.join(self.settings.name_folder_with_migrations,
                                                      'migrations')
        # self.init_migrate()

    # def migrate(self):
    #     self.schema.make_current_state_schema()

    def create_and_upgrade_all(self):
        self.upgrade()
        self.upload()

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

    def downgrade(self, downgrade_to_migration):
        migrations = Migrations(self.settings_migrations)
        migration = migrations.migrations.get(downgrade_to_migration, None)
        if migration is None:
            print('Not exist this migration to downgrade')
            return
        self.schema = Schema(self.db_connect,
                             self.settings_migrations)
        migration = self.schema.get_schema_to_downgrade(downgrade_to_migration)
        if migration.empty():
            print('State of migration to which it is necessary to downgrade conform to the current state')
            return
        migration.save_migration()



