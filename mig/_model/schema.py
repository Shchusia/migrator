from pprint import pprint
from .model import Column, Reference, Table
from _utils.helper import get_class_name
import os
from termcolor import colored
import traceback
from _utils.helper import download_json
from _model.model import TableSchema, ColumnSchema


class Schema(object):
    def __init__(self,
                 db_instance,
                 settings_migration,
                 is_print_sub_classes=False):
        self.subclasses = dict()
        self.get_sub_classes()
        if is_print_sub_classes:
            self.print_sub_classes()
        self.settings_migration = settings_migration
        self.settings_global = self.settings_migration.settings_global
        self.db_instance = db_instance
        self.current_state_schema = SchemaCurrentState(self.db_instance)
        self.migration_state_schema = SchemaFileState(self.db_instance,
                                                      self.settings_migration)

    def get_sub_classes(self):
        self.subclasses = {cls.__name__: cls for cls in Schema.__subclasses__()}

    def print_sub_classes(self):
        pprint(self.subclasses)

    def make_current_state_schema(self):
        self.current_state_schema.make_schema_by_classes(self.subclasses)

    def get_current_schema(self, with_objects=True):
        self.current_state_schema.make_schema_by_classes(self.subclasses,
                                                         with_objects)
        return self.current_state_schema.current_schema

    def get_migrations_schema(self):
        # print(self.migration_state_schema.get_files_migrations())
        self.migration_state_schema.make_schema_by_files()


class SchemaFileState(object):
    def __init__(self, db_instance, settings_migration):
        self.db_instance = db_instance
        self.settings_migration = settings_migration
        self.files_migration = self.get_files_migrations()
        self.dict_tables = dict()

    def get_files_migrations(self):
        try:
            files_migration = os.listdir(self.settings_migration.settings_global.folder_migrations)
        except:
            print(colored('Alarm failed to get files', 'red'))
            traceback.print_exc()
            files_migration = list()
        return files_migration

    def apply_migration(self, schema):
        def create(schema_create):
            for name_table, data_columns in schema_create.items():
                tmp_table = TableSchema(name_table, data_columns)
                self.dict_tables[name_table] = tmp_table

        def add(schema_add):
            for name_table, data_columns in schema_add.items():
                table = self.dict_tables[name_table]
                table.append_columns(data_columns)
                self.dict_tables[name_table] = table

        def upgrade(schema_upgrade):
            for name_table, data_columns in schema_upgrade.items():
                table = self.dict_tables[name_table]
                table.upgrade_columns(data_columns)
                self.dict_tables[name_table] = table

        def drop(schema_drop):
            for name_table, data_columns in schema_drop.items():
                if data_columns:
                    table = self.dict_tables[name_table]
                    table.drop_columns(data_columns)
                    self.dict_tables[name_table] = table
                else:
                    del self.dict_tables[name_table]

        create(schema['schema']['create'])
        add(schema['schema']['add'])
        upgrade(schema['schema']['upgrade'])
        drop(schema['schema']['drop'])

    def make_schema_by_files(self):
        def search_schema_where_previous_migration_is(name_previous_migration, dict_migrations):
            for value in dict_migrations.values():
                if value["previous_migration"] == name_previous_migration:
                    return value["current_migration"]
            return None

        dict_files = dict()
        for file in self.files_migration:
            tmp_dict = download_json(os.path.join(self.settings_migration.settings_global.folder_migrations, file))
            print(tmp_dict)
            dict_files[tmp_dict["current_migration"]] = tmp_dict
            """
            "previous_migration": null,
            "current_migration": "1587556241_56ff91329f",
            """
        # get first migration for start apply commits
        current_migration = search_schema_where_previous_migration_is(None,
                                                                      dict_files)

        # block for apply
        while True:
            tmp_migration = dict_files.get(current_migration, None)
            if tmp_migration is None:
                break
            self.apply_migration(tmp_migration)
            next_migration = search_schema_where_previous_migration_is(current_migration,
                                                                       dict_files)
            current_migration = next_migration  # stupid row for understand logic


        for table in self.dict_tables:
            print(self.dict_tables[table])





class SchemaCurrentState(object):
    def __init__(self, db_instance, ):
        self.db_instance = db_instance
        self.current_schema = dict()
        self.tables = dict()
    # TODO add to result schema list queue create tables

    def make_schema_by_classes(self,
                               subclasses,
                               with_objects=True):
        """
        dict class_name: cls
        :param subclasses:
        :param with_objects
        :return:
        """
        migration_schema = dict()
        tables_dict = dict()
        for clazz in subclasses.keys():
            current_class = subclasses[clazz]
            name_table = get_class_name(current_class)
            table = Table(name_table)
            # print(name_table)
            # print('#######')
            schema_table = dict()
            for attribute, value in current_class.__dict__.items():
                if isinstance(value, Column):
                    value.set_column_name(attribute)
                    res = value.make_schema(with_object=with_objects)
                    schema_table[attribute] = res
                    table.append_column(value)
            tables_dict[name_table] = table
            migration_schema[name_table] = schema_table

        Reference.check_correct_references_in_schema(migration_schema)
        self.current_schema = migration_schema
        self.tables = tables_dict
        return self.current_schema, self.tables



