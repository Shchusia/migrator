import os
from _model.schema import Schema
import sys
from _utils.utils import Settings
import psycopg2

class Migrate:
    def __init__(self, db_connect=None, settings_file=None, name_main_folder='migrations'):
        self.db_connect = db_connect
        self.settings_file = settings_file
        self.settings = Settings(settings_file)
        if not self.settings.is_exist_settings():
            self.init_migrate(name_main_folder=name_main_folder)
            self.settings.create_settings(name_main_folder)
        # self.init_migrate()

    @staticmethod
    def init_migrate(path_to_launcher='', name_main_folder='migrations'):
        # TODO make method for create file settings
        name_folder_with_migrations = 'migrations'
        if not os.path.isdir(name_main_folder):
            os.makedirs(name_main_folder)
        folder_migrations = os.path.join(name_main_folder, name_folder_with_migrations)
        os.makedirs(folder_migrations,
                    exist_ok=True)

    def migrate(self):
        schema = Schema()
        schema.get_sub_classes()
        print(schema.subclasses)

    def init(self):
        """
        проверяет если нет миграций в файле и в базе то создает первую миграцию
        если есть то ничего не делает

        :return:
        """
        pass


