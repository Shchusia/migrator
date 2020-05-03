import os

from migrant.connect.connect import Connect
from migrant.connect.db_adaptation.db_util import DbUtil
from migrant.migrations.migration import Migration
from migrant.migrations.migrations import MigrationsApplyToDb, \
    FileStoryMigrations, \
    StatusMigrations
from migrant.model.schema import SchemaMaker
from .settings import Settings


class Migrate:
    """
    Main class migrate
    """

    def __init__(self,
                 db_connect=None,
                 settings_file='migrate.yaml'):
        """

        :param db_connect:
        :param settings_file:
        """
        self.settings = Settings(settings_file)
        self.settings_project = self.settings.get_settings_project()
        self.settings_migrations = self.settings.get_settings_migrations()

        if db_connect is not None:
            if isinstance(db_connect, Connect):
                self.db_connect = db_connect.get_instance()
            elif isinstance(db_connect, DbUtil):
                self.db_connect = db_connect
            else:
                raise TypeError('db_connect must be extand class DbUtil')
        if db_connect is None and hasattr(self.settings_project, 'engine_str'):
            db_connect = Connect(getattr(self.settings_project, 'engine_str'))
            self.db_connect = db_connect.get_instance()
        elif db_connect is None:
            self.db_connect = db_connect
        else:
            self.settings_project.engine_str = self.db_connect.make_str_connect_engine()

        self.schema = SchemaMaker(db_instance=self.db_connect,
                                  settings=self.settings,
                                  is_print_sub_classes=False)

    @staticmethod
    def is_existed_files_in_folder(path_to_migrations_folder):
        return len(os.listdir(path_to_migrations_folder)) > 0

    def create_and_update(self):
        self.schema.make_tables()
        if Migrate.is_existed_files_in_folder(self.settings_project.folder_migrations):
            migration = self.schema.get_migration_difference_previous_and_current_state()
            if migration.empty():
                print('Any data to migrate')
            else:
                migration.save_migration()
        else:
            print('start init migrations')
            migration = Migration(self.settings_project)
            schema_to_insert = self.schema.get_current_schema()
            migration.first_migration(schema_to_insert)

    def upload(self):
        if self.db_connect is None:
            raise ValueError("No connection to the database")
        migration_db = MigrationsApplyToDb(
            self.db_connect,
            self.settings_project)
        migration_db.make_transactions()

    def upgrade(self):
        if not Migrate.is_existed_files_in_folder(self.settings_project.folder_migrations):
            print('start init migrations in upgrade command')
            migration = Migration(self.settings_project)
            schema_to_insert = self.schema.get_current_schema()
            migration.first_migration(schema_to_insert)
            return
        self.schema.make_tables()
        migration = self.schema.get_migration_difference_previous_and_current_state()
        if migration.empty():
            print('Any data to migrate')
        else:
            migration.save_migration()

    def downgrade(self, downgrade_to_migration):
        migrations = FileStoryMigrations(self.settings_project)
        migration = migrations.migrations.get(downgrade_to_migration, None)
        if migration is None:
            print('Not exist this migration to downgrade')
            return
        self.schema = SchemaMaker(self.db_connect,
                                  self.settings)
        migration = self.schema.get_schema_to_downgrade(downgrade_to_migration)
        if migration.empty():
            print('State of migration to which it is necessary to downgrade conform to the current state')
            return
        migration.save_migration()

    def get_status(self, command):
        commands_which_work_with_db = ['db', 'diff']
        if command in commands_which_work_with_db and self.db_connect is None:
            raise ValueError("No connection to the database")
        status_migr = StatusMigrations(self.settings_project, self.db_connect)
        if command == 'db':
            last_migration_in_db = status_migr.get_last_db_migration()
            print(last_migration_in_db)
        elif command == 'diff':
            last_migration_in_db = status_migr.get_last_db_migration()
            last_migration_in_storage = status_migr.get_last_storage_migration()
            print(last_migration_in_storage, last_migration_in_db)
            if last_migration_in_storage == last_migration_in_db:
                print('All migrations is applying to db')
            else:
                status_migr.diff_storage_and_db(last_migration_in_db,
                                                last_migration_in_storage)
        elif command == 'storage':
            last_migration_in_storage = status_migr.get_last_storage_migration()
            print(last_migration_in_storage)
        else:
            raise ValueError('Unknown command')
