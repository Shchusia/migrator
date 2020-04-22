import hashlib
import time
import datetime
import platform
from _utils.helper import save_to_json
import os


class Migration(object):
    structure_file = {
        'previous_migration': None,
        'current_migration': '',
        'comment': '',
        'date': '',
        'who_make_migration': '',
        'schema': dict()
    }

    def __init__(self, settings):
        self.settings = settings

    @staticmethod
    def get_name():
        str_name = '{}'.format(int(time.time()))
        hash_name = hashlib.md5(str_name.encode('utf-8')).hexdigest()[:10]
        return str_name + '_' + hash_name

    @staticmethod
    def get_who_make_migration():
        return platform.node()

    def init_migration(self,
                       schema_to_insert,
                       comment='init migration'):
        self.structure_file['current_migration'] = Migration.get_name()
        self.structure_file['date'] = datetime.datetime.now().isoformat()
        self.structure_file['comment'] = comment
        self.structure_file['who_make_migration'] = Migration.get_who_make_migration()
        self.structure_file['schema']['create'] = schema_to_insert
        self.structure_file['schema']['add'] = dict()
        self.structure_file['schema']['upgrade'] = dict()
        self.structure_file['schema']['drop'] = dict()
        path_to_save = os.path.join(self.settings.name_folder_with_migrations,
                                    self.settings.name_sub_folder_with_migrations,
                                    self.structure_file['current_migration'] + '.json')
        save_to_json(self.structure_file, path_to_save)



if __name__ == '__main__':
    print(Migration.get_name())
