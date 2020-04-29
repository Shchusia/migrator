import os
import yaml
from migrant import module_name


class SettingsInterface:
    """
    Interface for implement in settings classes migration & project
    """
    attributes_to_ignore = [
        'default_settings',
        'attributes_to_ignore',
        'settings_global',
        'folder_migrations',
        'path',
        'settings_migrations'
    ]

    @property
    def name_settings_file(self):
        raise NotImplementedError

    @property
    def default_settings(self):
        raise NotImplementedError

    @staticmethod
    def is_exist_settings(path: str):
        """
        method for check existed file
        :param path: path to file
        :return: bool is exist settings
        """
        return os.path.exists(path)

    @staticmethod
    def get_path_to_file(path: str):
        folders = path.split(os.sep)
        if len(folders) > 1:
            return os.path.join(*folders[:-1])
        return ''

    def _save(self, path, data):
        with open(path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file)
        self.__save_as_attributes(data)

    def get_settings(self,
                     path):
        with open(path, 'r', encoding='utf-8') as file:
            data = yaml.load(file)
        if not data:
            raise ValueError('not exist settings file')
        new_settings = self.default_settings.copy()
        new_settings.update(data)
        self.__save_as_attributes(new_settings)

    def __save_as_attributes(self, data):
        for name_attribute in data:
            if name_attribute != 'settings_file':
                self.__setattr__(name_attribute, data[name_attribute])

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
            self._save(self.name_settings_file, data_to_save)

    def __del__(self):
        self.save_state_settings()


class GeneratorPyFile:
    """
    class for make .py file for work with migrations without run project
    """
    name_py_file = '__main__.py'

    text_file = """import os
import sys
from {name_module} import CommandsHandler


path_to_settings_project = os.path.join(os.path.dirname(__file__), '..', )
sys.path.insert(0, path_to_settings_project)

# Please import your schemas
# ### in this block ###

# #####################


if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")

if __name__ == '__main__':
    CommandsHandler(sys.argv, path_to_launcher=os.path.abspath(__file__))
    
    """

    def __init__(self,
                 path_to_settings_file,
                 name_main_folder_migration):
        self.path_to_file = os.path.join(path_to_settings_file,
                                         name_main_folder_migration,
                                         self.name_py_file)
        if os.path.exists(self.path_to_file):
            pass
        else:
            self.create_file()

    def create_file(self):
        with open(self.path_to_file, 'w', encoding='utf-8') as py_file:
            py_file.write(self.text_file.format(name_module=module_name))


class SettingsProject(SettingsInterface):
    default_settings = {
        'name_folder_with_migrations': 'migrations',
        'name_sub_folder_with_migrations': 'migrations',
        'is_save_migrations_to_db': True,
        'name_db': 'migrations',
        'last_engine_str:': ''

    }
    name_settings_file = 'migrate.yaml'

    def __init__(self, name_settings_file=name_settings_file):
        self.settings_file = name_settings_file
        self.path = self.get_path_to_file(self.settings_file)
        self.folder_migrations = self.path
        if self.is_exist_settings(self.settings_file):
            self.get_settings(self.settings_file)
        else:
            self.create_settings()
        self.remake_if_not_exist()
        self.settings_migrations = SettingsMigrations(self)

    def remake_if_not_exist(self):

        os.makedirs(os.path.join(self.path,
                                 getattr(self,
                                         'name_folder_with_migrations')),
                    exist_ok=True)
        os.makedirs(self.folder_migrations,
                    exist_ok=True)
        GeneratorPyFile(self.path, self.default_settings['name_folder_with_migrations'])

    def create_settings(self):
        os.makedirs(os.path.join(self.path,
                                 self.default_settings['name_folder_with_migrations']),
                    exist_ok=True)
        folder_migrations = os.path.join(self.path,
                                         self.default_settings['name_folder_with_migrations'],
                                         self.default_settings['name_sub_folder_with_migrations'])
        os.makedirs(folder_migrations,
                    exist_ok=True)
        self.folder_migrations = folder_migrations
        self._save(self.settings_file,
                   self.default_settings)

    def get_settings(self, path_to_settings_file):
        super().get_settings(path_to_settings_file)

        folder_migrations = os.path.join(self.path,
                                         getattr(self,
                                                 'name_folder_with_migrations',
                                                 self.default_settings['name_folder_with_migrations']),
                                         getattr(self,
                                                 'name_sub_folder_with_migrations',
                                                 self.default_settings['name_sub_folder_with_migrations']))
        self.folder_migrations = folder_migrations

    def get_settings_migration(self):
        return self.settings_migrations


class SettingsMigrations(SettingsInterface):
    default_settings = {
        'last_commit': None,
        'is_drop_existed_tables_in_db_if_dont_exist_migration_table': False,
        'is_roll_back_transactions_to_existed_in_db': False,  # TODO implement this functionality
        'table_to_save_migrations_store': 'story_migrations',
        'name_key_column': 'current_migration',
        'is_drop_then_create_new_for_update_column_table': True,
    }
    name_settings_file = 'settings.yaml'

    def __init__(self, settings_project: SettingsProject):
        if not isinstance(settings_project, SettingsProject):
            raise TypeError('Incorrect type settings_project argument in __init__ SettingsMigrations')
        self.name_settings_file = os.path.join(settings_project.path,
                                               settings_project.name_folder_with_migrations,
                                               self.name_settings_file)
        if self.is_exist_settings(self.name_settings_file):
            self.get_settings(self.name_settings_file)
        else:
            self.create_settings()

    def create_settings(self):
        self._save(self.name_settings_file, self.default_settings)


class Settings:
    """
    class for load settings or create if not exist

    """
    def __init__(self, project_settings_file=SettingsProject.name_settings_file):
        self.settings_project = SettingsProject(project_settings_file)
        self.settings_migrations = self.settings_project.get_settings_migration()

    def get_settings_migrations(self):
        return self.settings_migrations

    def get_settings_project(self):
        return self.settings_project


if __name__ == '__main__':
    pass
    # name = (os.path.abspath(os.path.dirname(__file__))).split(os.sep)[-1]
    #
    # print(name)
    # print(os.path.abspath(os.path.dirname(__file__)))
    # SettingsMigrations('')