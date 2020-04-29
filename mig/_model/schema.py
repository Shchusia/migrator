from pprint import pprint
from .model import Column, Reference, Table
from _utils.helper import get_class_name
import os
from termcolor import colored
import traceback
from _utils.helper import download_json
from _model.model import TableSchema
from _migrate.migration import Migration
from _migrate.migration import Migrations




class SchemaInterface(object):
    dict_tables = dict()
    schema = dict()

    def make_tables(self, *args, **kwargs):
        raise NotImplementedError

    def make_schema_by_tables(self):
        raise NotImplementedError

    def get_tables_dict(self):
        return self.dict_tables


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

    # def make_current_state_schema(self):
    #     self.current_state_schema.make_tables(self.subclasses)
    #     return self.current_state_schema.make_schema_by_tables()

    def get_current_schema(self, with_objects):
        self.current_state_schema.make_tables(self.subclasses)
        return self.current_state_schema.make_schema_by_tables()
        # self.current_state_schema.make_schema_by_classes(self.subclasses,
        #                                                  with_objects)
        # return self.current_state_schema.current_schema

    def get_migrations_schema(self):
        # print(self.migration_state_schema.get_files_migrations())
        return self.migration_state_schema.make_tables()

    def make_tables(self):
        print('Start make tables from classes')
        self.current_state_schema.make_tables(self.subclasses)
        print('Start make tables from files')
        self.migration_state_schema.make_tables()

    def compare_tables(self, dict_table_migrations, dict_table_current):
        if not dict_table_migrations or not dict_table_current:
            raise Warning('one of dict tables is empty')
        new_migration = Migration(self.settings_global)
        new_migration.set_previous_migration(self.migration_state_schema.last_migration)
        tables_mig = set(dict_table_migrations.keys())
        tables_cur = set(dict_table_current.keys())

        droped_tables = tables_mig - tables_cur
        new_tables = tables_cur - tables_mig
        intersection_tables = tables_mig & tables_cur
        # add new tables to migration
        for name_table in new_tables:
            new_migration.append_to_create(name_table,
                                           dict_table_current[name_table].make_schema(with_name_column=False,
                                                                                      with_object=False))
        # add tables to drop
        for name_table in droped_tables:
            new_migration.append_to_drop(name_table)

        for name_table in intersection_tables:
            result = dict_table_current[name_table].compare_with_table(dict_table_migrations[name_table])
            if result:
                if result['drop']:
                    for columns_name, column_to_drop in result['drop'].items():
                        new_migration.append_to_drop(name_table, column_to_drop)
                if result['add']:
                    for columns_name, column_to_add in result['add'].items():
                        new_migration.append_to_add(name_table, column_to_add)
                if result['upgrade']:
                    for columns_name, column_to_upgrade in result['upgrade'].items():
                        new_migration.append_to_upgrade(name_table, column_to_upgrade)
            else:
                continue
        return new_migration

    def get_migration_difference_previous_and_current_state(self):
        dict_table_migrations = self.migration_state_schema.get_tables_dict()
        dict_table_current = self.current_state_schema.get_tables_dict()
        return self.compare_tables(dict_table_migrations, dict_table_current)
        # if not dict_table_migrations or not dict_table_current:
        #     raise Warning('one of dict tables is empty')
        # new_migration = Migration(self.settings_global)
        # new_migration.set_previous_migration(self.migration_state_schema.last_migration)
        # tables_mig = set(dict_table_migrations.keys())
        # tables_cur = set(dict_table_current.keys())
        #
        # droped_tables = tables_mig - tables_cur
        # new_tables = tables_cur - tables_mig
        # intersection_tables = tables_mig & tables_cur
        # # add new tables to migration
        # for name_table in new_tables:
        #     new_migration.append_to_create(name_table,
        #                                    dict_table_current[name_table].make_schema(with_name_column=False,
        #                                                                               with_object=False))
        # # add tables to drop
        # for name_table in droped_tables:
        #     new_migration.append_to_drop(name_table)
        #
        # for name_table in intersection_tables:
        #     result = dict_table_current[name_table].compare_with_table(dict_table_migrations[name_table])
        #     if result:
        #         if result['drop']:
        #             for columns_name, column_to_drop in result['drop'].items():
        #                 new_migration.append_to_drop(name_table, column_to_drop)
        #         if result['add']:
        #             for columns_name, column_to_add in result['add'].items():
        #                 new_migration.append_to_add(name_table, column_to_add)
        #         if result['upgrade']:
        #             for columns_name, column_to_upgrade in result['upgrade'].items():
        #                 new_migration.append_to_upgrade(name_table, column_to_upgrade)
        #     else:
        #         continue
        # return new_migration

    def get_schema_to_downgrade(self, name_to_downgrade):
        full_schema_by_files = SchemaFileState(self.db_instance,
                                               self.settings_migration)
        print('Restore the state of the circuit {} migration'.format(name_to_downgrade))
        self.migration_state_schema.make_tables(migration_to_which_perform=name_to_downgrade)
        print('Start make full tables from migrations')
        full_schema_by_files.make_tables()
        dict_table_migrations = self.migration_state_schema.get_tables_dict()
        dict_table_current = full_schema_by_files.get_tables_dict()
        migration_downgrade = self.compare_tables(dict_table_migrations, dict_table_current)
        migration_downgrade.set_comment_migration('Downgrade state to migration {}'.format(name_to_downgrade))
        migration_downgrade.set_previous_migration(self.migration_state_schema.get_last_migration_in_states())
        return migration_downgrade


class SchemaFileState(SchemaInterface):

    def __init__(self, db_instance, settings_migration):
        self.db_instance = db_instance
        self.settings_migration = settings_migration
        self.migrations = Migrations(settings_migration)
        self.files_migration = self.migrations.get_files_migrations()
        self.dict_tables = dict()
        self.last_migration = None

    def get_last_migration_in_states(self):
        current_migration = self.migrations.search_schema_where_previous_migration_is(None)
        while True:
            tmp_migration = self.migrations.get_migration_by_name_migration(current_migration)
            if tmp_migration is None:
                break
            current_migration = self.migrations.search_schema_where_previous_migration_is(current_migration)
        return current_migration

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

    # def make_schema_by_files(self):
    #     def search_schema_where_previous_migration_is(name_previous_migration, dict_migrations):
    #         for value in dict_migrations.values():
    #             if value["previous_migration"] == name_previous_migration:
    #                 return value["current_migration"]
    #         return None
    #
    #     dict_files = dict()
    #     for file in self.files_migration:
    #         tmp_dict = download_json(os.path.join(self.settings_migration.settings_global.folder_migrations, file))
    #         # print(tmp_dict)
    #         dict_files[tmp_dict["current_migration"]] = tmp_dict
    #         """
    #         "previous_migration": null,
    #         "current_migration": "1587556241_56ff91329f",
    #         """
    #     # get first migration for start apply commits
    #     current_migration = search_schema_where_previous_migration_is(None,
    #                                                                   dict_files)
    #     # block for apply
    #     self.last_migration = current_migration
    #     while True:
    #         tmp_migration = dict_files.get(current_migration, None)
    #         if tmp_migration is None:
    #             break
    #         self.last_migration = current_migration
    #         self.apply_migration(tmp_migration)
    #         next_migration = search_schema_where_previous_migration_is(current_migration,
    #                                                                    dict_files)
    #         current_migration = next_migration  # stupid row for understand logic

    def make_tables(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:  must have make_schema_to_migration for downgrade state
        :return:
        """
        # def search_schema_where_previous_migration_is(name_previous_migration, dict_migrations):
        #     for value in dict_migrations.values():
        #         if value["previous_migration"] == name_previous_migration:
        #             return value["current_migration"]
        #     return None
        #
        # dict_files = dict()
        # for file in self.files_migration:
        #     tmp_dict = download_json(os.path.join(self.settings_migration.settings_global.folder_migrations, file))
        #     dict_files[tmp_dict["current_migration"]] = tmp_dict
        # get first migration for start apply commits
        # current_migration = search_schema_where_previous_migration_is(None,
        #                                                               dict_files)

        migration_to_which_perform = None
        if len(args):
            migration_to_which_perform = args[0]
        if kwargs.get('migration_to_which_perform', None) is not None:
            migration_to_which_perform = kwargs['migration_to_which_perform']
        # print(make_schema_to_migration)
        current_migration = self.migrations.search_schema_where_previous_migration_is(None)
        # print(migration_to_which_perform)
        # block for apply
        while True:
            tmp_migration = self.migrations.get_migration_by_name_migration(current_migration)
            if tmp_migration is None:
                break
            self.last_migration = current_migration
            self.apply_migration(tmp_migration)
            if migration_to_which_perform == current_migration:
                # print('break')
                break
            next_migration = self.migrations.search_schema_where_previous_migration_is(current_migration,
                                                                                       )
            current_migration = next_migration  # stupid row for understand logic

    def make_schema_by_tables(self):
        raise NotImplementedError


class SchemaCurrentState(SchemaInterface):

    def __init__(self, db_instance, ):
        self.db_instance = db_instance
        self.current_schema = dict()

    # TODO add to result schema list queue create tables

    def make_tables(self, *args, **kwargs):
        subclasses = args[0] if len(args) > 0 else kwargs.get('subclasses')
        self.subclasses = subclasses
        print(self.subclasses)
        tables_dict = dict()
        for clazz in subclasses.keys():
            current_class = subclasses[clazz]
            name_table = get_class_name(current_class)
            table = Table(name_table)
            if tables_dict.get(name_table, None) is not None:
                raise AttributeError('You want create 2(or more) tables with one name "{}" '.format(name_table))
            for attribute, value in current_class.__dict__.items():
                if isinstance(value, Column):
                    value.set_column_name(attribute)
                    table.append_column(value)
            tables_dict[name_table] = table
        self.dict_tables = tables_dict

    def make_schema_by_tables(self):
        if not self.dict_tables:
            print('Empty dict existed tables we try make tables')
            return
        schema_tables = dict()
        for name_table, table in self.dict_tables.items():
            schema_tables[name_table] = table.make_schema(with_object=False, with_name_column=False)
        print(schema_tables)
        Reference.check_correct_references_in_schema(schema_tables)

        self.schema = schema_tables
        return self.schema

    # def make_schema_by_classes(self,
    #                            subclasses,
    #                            with_objects=True):
    #     """
    #     !!! DEPRECATED method
    #     dict class_name: cls
    #     :param subclasses:
    #     :param with_objects
    #     :return:
    #     """
    #     migration_schema = dict()
    #     tables_dict = dict()
    #     for clazz in subclasses.keys():
    #         # print(clazz)
    #         current_class = subclasses[clazz]
    #         name_table = get_class_name(current_class)
    #         table = Table(name_table)
    #         schema_table = dict()
    #         for attribute, value in current_class.__dict__.items():
    #             if isinstance(value, Column):
    #                 value.set_column_name(attribute)
    #                 res = value.make_schema(with_object=with_objects)
    #                 schema_table[attribute] = res
    #                 table.append_column(value)
    #         tables_dict[name_table] = table
    #         migration_schema[name_table] = schema_table
    #
    #     # Reference.check_correct_references_in_schema(migration_schema)
    #     self.current_schema = migration_schema
    #     self.dict_tables = tables_dict
    #     # return self.current_schema, self.tables
