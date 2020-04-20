import yaml
import os


class Settings(object):
    name_sub_folder_with_migrations = 'migrations'
    default_settings = {
        'name_folder_with_migrations': 'migrations',
        'is_save_migrations_to_db': True,
        'name_db': 'migrations',

    }

    def __init__(self,
                 name_file=None):
        if name_file:
            self.settings_file = name_file
        else:
            self.settings_file = 'migrate.yaml'
        if self.is_exist_settings():
            self.get_settings()
        else:
            self.create_settings()

    def is_exist_settings(self):
        return os.path.exists(self.settings_file)

    def __save_settings(self, data):
        for name_attribute in data:
            self.__setattr__(name_attribute, data[name_attribute])

    def create_settings(self):
        with open(self.settings_file, 'w') as file:
            yaml.dump(self.default_settings, file)
        self.__save_settings(self.default_settings)


        os.makedirs(self.name_folder_with_migrations, exist_ok=True)
        folder_migrations = os.path.join(self.name_folder_with_migrations, self.name_sub_folder_with_migrations )
        os.makedirs(folder_migrations,
                    exist_ok=True)

    def get_settings(self):
        data = dict()
        with open(self.settings_file) as f:
            data = yaml.load(f,)
        # print(data)
        if not data:
            raise ValueError('not exist settings file')
        self.__save_settings(data)
