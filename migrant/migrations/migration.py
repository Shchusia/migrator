import datetime
import hashlib
import os
import platform
import time

from migrant._utils.helper import save_to_json
from migrant.model.model import TableSchema, ColumnSchema


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


class MigrationToImplement:
    attributes_to_ignore = [
        'attributes_to_ignore',
        'queries_to_run',
        'settings_migrations'
    ]

    def __init__(self,
                 previous_migration,
                 current_migration,
                 comment,
                 date,
                 who_make_migration,
                 schema,
                 settings_migrations):
        self.previous_migration = previous_migration
        self.current_migration = current_migration
        self.comment = comment
        self.date = date
        self.who_make_migration = who_make_migration
        self.schema = schema
        self.queries_to_run = list()
        self.settings_migrations = settings_migrations

    def __str__(self):
        return '<Migration {} >'.format(self.current_migration)

    def make_insert_row_migration(self, db_instance):

        def create_tables(to_create_tables):
            list_crete_table = list()
            for name_table, columns in to_create_tables.items():
                table = TableSchema(name_table, columns)
                create_select = table.make_create_table_request(db_instance)
                list_crete_table.append(create_select)
            return list_crete_table

        def alter_columns_to_table(action_columns, action):
            list_alter_table_add = list()
            for name_table in action_columns.keys():
                for column_name, column_data in action_columns[name_table].items():
                    column_tmp = ColumnSchema(**column_data)
                    add_column = column_tmp.alter_table(name_table=name_table,
                                                        alter_action=action,
                                                        db_instance=db_instance,
                                                        is_recreate_column_to_update=getattr(self.settings_migrations,
                                                                                             'is_drop_then_create_new_'
                                                                                             'for_update_column_table',
                                                                                             False))
                    list_alter_table_add.extend(add_column)
            return list_alter_table_add

        def drop_tables(to_drop):
            list_to_drop = list()
            for name_table in to_drop.keys():
                if to_drop[name_table]:
                    # drop columns
                    for column_name, column_data in to_drop[name_table].items():
                        column_tmp = ColumnSchema(**column_data)
                        add_column = column_tmp.alter_table(name_table, 'drop', db_instance)
                        list_to_drop.extend(add_column)
                else:
                    list_to_drop.append(TableSchema.drop_table(name_table))
            return list_to_drop

        self.queries_to_run.extend(create_tables(self.schema["create"]))
        self.queries_to_run.extend(alter_columns_to_table(self.schema["add"],
                                                          'add'))
        self.queries_to_run.extend(alter_columns_to_table(self.schema["upgrade"],
                                                          'upgrade'))
        self.queries_to_run.extend(drop_tables(self.schema["drop"]))

    def get_queries(self, db_instance):
        self.make_insert_row_migration(db_instance)
        return self.queries_to_run

    def get_data_to_save_in_db(self):
        data_to_save = dict()
        for attribute in dir(self):
            if attribute in self.attributes_to_ignore or attribute[1] == '_':
                continue
            elif callable(getattr(self, attribute)):
                continue
            data_to_save[attribute] = getattr(self, attribute)
        return data_to_save
