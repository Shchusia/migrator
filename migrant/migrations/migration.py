import datetime
import hashlib
import os
import platform
import time

from migrant._utils.helper import save_to_json


class Migration(object):
    structure_file = {
        'previous_migration': None,
        'current_migration': '',
        'comment': '',
        'date': '',
        'who_make_migration': '',
        'schema': {
            'create': dict(),  # only for table
            'add': dict(),  # new columns
            'upgrade': dict(),  # for columns is new state column
            'drop': dict(),  # for tables and columns if table don't have any parameters is drop table
            # another name column to drop
        }
    }

    def __init__(self, settings):
        self.settings = settings
        self.init_migration()

    def empty(self):
        return not (self.structure_file['schema']['create']
                    or self.structure_file['schema']['add']
                    or self.structure_file['schema']['upgrade']
                    or self.structure_file['schema']['drop'])

    @staticmethod
    def get_name():
        str_name = '{}'.format(int(time.time()))
        hash_name = hashlib.md5(str_name.encode('utf-8')).hexdigest()[:10]
        return str_name + '_' + hash_name

    @staticmethod
    def get_who_make_migration():
        return platform.node()

    def set_previous_migration(self, name_previous_migration=None):
        self.structure_file['previous_migration'] = name_previous_migration

    def set_comment_migration(self, comment):
        self.structure_file['comment'] = comment

    def init_migration(self):
        self.structure_file['current_migration'] = Migration.get_name()
        self.structure_file['date'] = datetime.datetime.now().isoformat()
        self.structure_file['who_make_migration'] = Migration.get_who_make_migration()

    def save_migration(self):
        path_to_save = os.path.join(self.settings.folder_migrations,
                                    self.structure_file['current_migration'] + '.json')
        print(path_to_save)
        save_to_json(self.structure_file, path_to_save)

    def first_migration(self,
                        schema_to_insert,
                        comment='init migration'):

        self.structure_file['comment'] = comment
        self.structure_file['schema']['create'] = schema_to_insert
        self.save_migration()

    def append_to_create(self, name_table, schema_table):
        self.structure_file['schema']['create'][name_table] = schema_table

    def append_to_concrete_action_schema(self, name_table, column=None, action='drop'):
        if column is None:
            self.structure_file['schema'][action][name_table] = dict()
        else:
            columns_to_action_table = self.structure_file['schema'][action].get(name_table, dict())
            columns_to_action_table[column.get_column_name()] = column.make_schema(with_object=False,
                                                                                   with_name_column=False)
            self.structure_file['schema'][action][name_table] = columns_to_action_table

    def append_to_add(self, name_table, column_to_add, ):
        self.append_to_concrete_action_schema(name_table, column_to_add, 'add')

    def append_to_upgrade(self, name_table, column_to_upgrade):
        self.append_to_concrete_action_schema(name_table, column_to_upgrade, 'upgrade')

    def append_to_drop(self, name_table, column_to_drop=None):
        self.append_to_concrete_action_schema(name_table, column_to_drop, 'drop')
        # if column_to_drop is None:
        #     self.structure_file['schema']['drop'][name_table] = dict()
        # else:
        #     columns_to_drop = self.structure_file['schema']['drop'].get(name_table, dict())
        #     columns_to_drop[column_to_drop.get_column_name()] = column_to_drop.make_schema()
        #     self.structure_file['schema']['drop'][name_table] = columns_to_drop
