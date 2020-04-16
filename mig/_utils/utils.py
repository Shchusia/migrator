import yaml
import os


class Settings(object):
    default_settings = {
        'is_save_migrations_to_db': True,
        'name_db': 'migrations',

    }

    def __init__(self, name_file=None):
        if name_file:
            self.name_file = name_file
        else:
            self.name_file = 'migrate.yaml'

    def is_exist_settings(self):
        return os.path.exists(self.name_file)

    def create_settings(self,
                        name_folder_with_migrations=''):
        data_to_insert = {
            'name_folder_with_migrations': name_folder_with_migrations
        }
        with open(self.name_file, 'w') as file:
            yaml.dump(data_to_insert, file)

    def get_settings(self):
        with open('items.yaml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            print(data)
