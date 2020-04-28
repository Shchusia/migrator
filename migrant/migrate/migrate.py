import os

from migrant.connect import Connect
from migrant.connect.db_adaptation.db_util import DbUtil
from migrant.model.schema import SchemaMaker
from .settings import Settings
from migrant.migrations.migration import Migration


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
        if db_connect is None and hasattr(self.settings_project, 'last_engine_str'):
            db_connect = Connect(getattr(self.settings_project, 'last_engine_str'))
            self.db_connect = db_connect.get_instance()
        elif db_connect is None:
            pass
        else:
            self.settings.last_engine_str = self.db_connect.make_str_connect_engine()
        self.db_connect = db_connect

        self.schema = SchemaMaker(db_instance=self.db_connect,
                                  settings=self.settings,
                                  is_print_sub_classes=True)

    def create_and_update(self):

        def is_existed_files_in_folder(path_to_migrations_folder):
            return len(os.listdir(path_to_migrations_folder)) > 0

        # print(path)
        self.schema.make_tables()
        if is_existed_files_in_folder(self.settings_project.folder_migrations):
            migration = self.schema.get_migration_difference_previous_and_current_state()
            if migration.empty():
                print('Any data to migrate')
            else:
                migration.save_migration()
        else:
            # TODO make got migrations from files
            print('start init migrations')
            migration = Migration(self.settings_project)
            schema_to_insert = self.schema.get_current_schema()
            migration.first_migration(schema_to_insert)








