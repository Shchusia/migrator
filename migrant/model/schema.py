from pprint import pprint
from migrant.migrations.migrations import FileStoryMigrations
from migrant.model.model import TableSchema, Column, Table, Reference
from migrant._utils.helper import get_class_name


class Schema:
    """
    A class to inherit the classes you want to migrate
    """
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

    @staticmethod
    def _get_sub_classes():
        return {cls.__name__: cls for cls in Schema.__subclasses__()}

    def print_sub_classes(self):
        pprint(self.subclasses)


class SchemaFileState:
    def __init__(self, settings_migration):
        self.settings_migration = settings_migration
        self.migrations = FileStoryMigrations(settings_migration)
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
        print(schema_tables)
        Reference.check_correct_references_in_schema(schema_tables)

        self.schema = schema_tables
        return self.schema
