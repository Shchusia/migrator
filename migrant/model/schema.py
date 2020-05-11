from pprint import pprint

from migrant._utils.helper import get_class_name
from migrant.migrations.migration import Migration
from migrant.migrations.migrations import FileStoryMigrations
from migrant.model.table import TableSchema, Table
from migrant.model.column import Column
from migrant.model.reference import Reference


class SchemaTable:
    def __init__(self, columns_table, **kwargs):
        self.columns = {col: None for col in columns_table}
        for attribute in self.columns:
            setattr(self, attribute, self.columns[attribute])
        for attribute in kwargs.keys():
            self.columns[attribute] = kwargs[attribute]
            setattr(self, attribute, kwargs[attribute])

    def __str__(self):
        res = '<Table: {columns}>'
        for column in self.columns:
            self.columns[column] = getattr(self, column)
        return res.format(columns=str(self.columns))

    def get_value(self, name_attribute):
        return self.columns.get(name_attribute, None)


class Schema:
    """
    A class to inherit the classes you want to migrate
    """

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_class(cls):
        return cls

    def __init__(self, *args, **kwargs):
        columns_table = list()
        for attribute in dir(self):
            if attribute == 'c' or attribute[1] == '_':
                continue
            elif callable(getattr(self, attribute)):
                continue
            columns_table.append(attribute)
        # print(columns_table)

        col = SchemaTable(columns_table, **kwargs)
        setattr(self, 'c', col)
        name_table = self.get_name()
        print(name_table)
        table = Table(name_table)
        for attribute, value in self.get_class().__dict__.items():
            # print(attribute)
            if isinstance(value, Column):
                value.set_column_name(attribute)
                value.set_value(col.get_value(attribute))
                table.append_column(value)
        self.table = table

    @classmethod
    def _get_col(cls):
        pass

    def get_table(self):
        return self.table

    def insert(self, *args, **kwargs):
        pass

    def delete(self):
        pass

    def update(self):
        pass

    def select(self):
        pass


class SchemaMaker:
    """
    Main class for make schemas from classes and files
    """

    def __init__(self,
                 db_instance,
                 settings,
                 is_print_sub_classes=False):
        self.subclasses = self._get_sub_classes()
        if is_print_sub_classes:
            self.print_sub_classes()
        self.settings_project = settings.get_settings_project()
        self.settings_migrations = settings.get_settings_migrations()
        self.db_instance = db_instance
        self.current_state_schema = SchemaCurrentState(self.subclasses)
        self.migration_state_schema = SchemaFileState(self.settings_project)

    @staticmethod
    def _get_sub_classes():
        return {cls.__name__: cls for cls in Schema.__subclasses__()}

    def print_sub_classes(self):
        pprint(self.subclasses)

    def make_tables(self):
        print('Start make tables from classes')
        self.current_state_schema.make_tables()
        print('Start make tables from files')
        self.migration_state_schema.make_tables()

    def compare_tables(self, dict_table_migrations, dict_table_current):
        # print(dict_table_migrations)
        # print(dict_table_current)
        if not dict_table_migrations or not dict_table_current:
            raise ValueError('one of dict tables is empty')
        new_migration = Migration(self.settings_project)
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

    def get_schema_to_downgrade(self, name_to_downgrade):
        full_schema_by_files = SchemaFileState(self.settings_project)
        print('Restore the state of the circuit {} migration'.format(name_to_downgrade))
        self.migration_state_schema.make_tables(migration_to_which_perform=name_to_downgrade)
        print('Start make full tables from migrations')
        full_schema_by_files.make_tables()
        dict_table_migrations = self.migration_state_schema.get_tables_dict()
        dict_table_current = full_schema_by_files.get_tables_dict()
        migration_downgrade = self.compare_tables(dict_table_current, dict_table_migrations)
        migration_downgrade.set_comment_migration('Downgrade state to migration {}'.format(name_to_downgrade))
        migration_downgrade.set_previous_migration(self.migration_state_schema.get_last_migration_in_states())
        return migration_downgrade

    def get_current_schema(self):
        if not self.current_state_schema.get_tables_dict():
            self.current_state_schema.make_tables()
        return self.current_state_schema.make_schema_by_tables()


class SchemaFileState:
    def __init__(self, settings_project):
        self.settings_project = settings_project
        self.migrations = FileStoryMigrations(settings_project)
        self.files_migration = self.migrations.get_files_migrations()
        self.dict_tables = dict()
        self.last_migration = None

    def get_last_migration_in_states(self):
        current_migration = self.migrations.search_schema_where_previous_migration_is(None)
        while True:
            tmp_migration = self.migrations.get_migration_by_name_migration(current_migration)
            if tmp_migration is None:
                break
            previous = self.migrations.search_schema_where_previous_migration_is(current_migration)
            if previous is None:
                break
            current_migration = previous
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

    def make_tables(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:  must have make_schema_to_migration for downgrade state
        :return:
        """

        migration_to_which_perform = None
        if len(args):
            migration_to_which_perform = args[0]
        if kwargs.get('migration_to_which_perform', None) is not None:
            migration_to_which_perform = kwargs['migration_to_which_perform']
        current_migration = self.migrations.search_schema_where_previous_migration_is(None)
        while True:
            tmp_migration = self.migrations.get_migration_by_name_migration(current_migration)
            if tmp_migration is None:
                break
            self.last_migration = current_migration
            self.apply_migration(tmp_migration)
            if migration_to_which_perform == current_migration:
                break
            next_migration = self.migrations.search_schema_where_previous_migration_is(current_migration,
                                                                                       )
            current_migration = next_migration  # stupid row for understand logic

    def make_schema_by_tables(self):
        raise NotImplementedError

    def get_tables_dict(self):
        return self.dict_tables


class SchemaCurrentState:
    def __init__(self, subclasses):
        self.subclasses = subclasses
        self.dict_tables = dict()
        self.schema = dict()

    def make_tables(self):
        tables_dict = dict()
        for clazz in self.subclasses.keys():
            current_class = self.subclasses[clazz]
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
        Reference.check_correct_references_in_schema(schema_tables)

        self.schema = schema_tables
        return self.schema

    def get_tables_dict(self):
        return self.dict_tables
