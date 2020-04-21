import yaml
import os
import inspect


class Settings(object):
    attributes_to_ignore = [
        'default_settings',
        'attributes_to_ignore',
        'settings_global'
    ]

    @property
    def settings_file(self):
        raise NotImplementedError

    def get_settings(self, path):
        with open(path) as f:
            data = yaml.load(f, )
        if not data:
            raise ValueError('not exist settings file')
        self.__save_as_attributes(data)

    def __save_as_attributes(self, data):
        for name_attribute in data:
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
        'last_commit': None
    }

    def __init__(self, settings_global):
        self.settings_global = settings_global
        self.settings_file = os.path.join(self.settings_global.name_folder_with_migrations, self.settings_file)
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
        self._save(self.settings_file,
                   self.default_settings)



