import yaml
import os
# import inspect


class Settings(object):
    attributes_to_ignore = [
        'default_settings',
        'attributes_to_ignore',
        'settings_global',
        'folder_migrations',
    ]

    @property
    def settings_file(self):
        raise NotImplementedError

    def get_settings(self, path):
        with open(path) as f:
            data = yaml.load(f, )
        if not data:
            raise ValueError('not exist settings file')
        new_settings = self.default_settings.copy()
        new_settings.update(data)
        self.__save_as_attributes(new_settings)

    def __save_as_attributes(self, data):
        for name_attribute in data:
            if name_attribute != 'settings_file':
                self.__setattr__(name_attribute, data[name_attribute])

    @staticmethod
    def is_exist_settings(path):
        return os.path.exists(path)

    def create_settings(self):
        raise NotImplementedError

    def save_state_settings(self):
        data_to_save = dict()
        for attribute in dir(self):
            if attribute in self.attributes_to_ignore or attribute[1] == '_':
                continue
            elif callable(getattr(self, attribute)):
                continue
            data_to_save[attribute] = getattr(self, attribute)
        if data_to_save:
            self._save(self.settings_file, data_to_save)

    def _save(self, path, data):
        with open(path, 'w') as file:
            yaml.dump(data, file)
        self.__save_as_attributes(data)

    def __del__(self):
        self.save_state_settings()


class SettingsMigrations(Settings):
    settings_file = 'settings.yaml'
    default_settings = {
        'last_commit': None,
        'is_drop_existed_tables_in_db_if_dont_exist_migration_table': False,
        'is_roll_back_transactions_to_existed_in_db': False,  # TODO implement this functionality
        'table_to_save_migrations_store': 'story_migrations',
        'name_key_column': 'current_migration'
    }

    def __init__(self, settings_global):
        self.settings_global = settings_global
        self.settings_file = os.path.join(self.settings_global.name_folder_with_migrations, self.settings_file)
        pathss = settings_global.settings_file.split(os.sep)
        if len(pathss) > 1:
            prath_to_folder_where_settings_file = os.path.join( *pathss[:-1])
            self.settings_file = os.path.join(prath_to_folder_where_settings_file, self.settings_file)
        if self.is_exist_settings(self.settings_file):
            self.get_settings(self.settings_file)
        else:
            self.create_settings()

    def create_settings(self):
        self._save(self.settings_file, self.default_settings)


class SettingsGlobal(Settings):
    name_sub_folder_with_migrations = 'migrations'
    default_settings = {
        'name_folder_with_migrations': 'migrations',
        'is_save_migrations_to_db': True,
        'name_db': 'migrations',

    }
    settings_file = 'migrate.yaml'

    def __init__(self,
                 name_file=None):
        if name_file:
            self.settings_file = name_file
        if self.is_exist_settings(self.settings_file):
            self.get_settings(self.settings_file)
        else:
            self.create_settings()

    def create_settings(self):
        os.makedirs(self.default_settings['name_folder_with_migrations'], exist_ok=True)
        folder_migrations = os.path.join(self.default_settings['name_folder_with_migrations'],
                                         self.name_sub_folder_with_migrations)
        os.makedirs(folder_migrations,
                    exist_ok=True)
        self.folder_migrations = folder_migrations
        self._save(self.settings_file,
                   self.default_settings)

    def get_settings(self, path):
        super().get_settings(path)
        pathss = self.settings_file.split(os.sep)
        folder_migrations = os.path.join(self.default_settings['name_folder_with_migrations'],
                                         self.name_sub_folder_with_migrations)
        if len(pathss) > 1:
            path_to_folder_where_settings_file = os.path.join(*pathss[:-1])
            folder_migrations= os.path.join(path_to_folder_where_settings_file, folder_migrations)

        self.folder_migrations = folder_migrations
