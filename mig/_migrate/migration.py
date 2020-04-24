import hashlib
import time
import datetime
import platform
from _utils.helper import save_to_json
import os
from _db_adaptation.db_util import DbUtil
from _utils.settings import SettingsMigrations
import traceback
from _utils.helper import download_json
from _model.model import TableSchema, \
    ColumnSchema


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

    def init_migration(self):
        self.structure_file['current_migration'] = Migration.get_name()
        self.structure_file['date'] = datetime.datetime.now().isoformat()
        self.structure_file['who_make_migration'] = Migration.get_who_make_migration()

    def save_migration(self):
        path_to_save = os.path.join(self.settings.name_folder_with_migrations,
                                    self.settings.name_sub_folder_with_migrations,
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
        # if column_to_drop is None:
        #     self.structure_file['schema']['drop'][name_table] = dict()
        # else:
        #     columns_to_drop = self.structure_file['schema']['drop'].get(name_table, dict())
        #     columns_to_drop[column_to_drop.get_column_name()] = column_to_drop.make_schema()
        #     self.structure_file['schema']['drop'][name_table] = columns_to_drop


class Migrations:
    """
    class for work with saved migrations
    """

    def __init__(self, settings_migration):
        self.settings_migration = settings_migration
        self.migrations = dict()
        self.download_all_migrations()

    def get_files_migrations(self):
        try:
            files_migration = os.listdir(self.settings_migration.settings_global.folder_migrations)
        except:
            traceback.print_exc()
            files_migration = list()
        return files_migration

    def download_all_migrations(self):
        for file in self.get_files_migrations():
            tmp_dict = download_json(os.path.join(self.settings_migration.settings_global.folder_migrations, file))
            self.migrations[tmp_dict["current_migration"]] = tmp_dict

    def get_migrations_dict(self):
        return self.migrations

    def search_schema_where_previous_migration_is(self, name_previous_migration):
        for value in self.migrations.values():
            if value["previous_migration"] == name_previous_migration:
                return value["current_migration"]
        return None

    def get_migration_by_name_migration(self, name_migration):
        return self.migrations.get(name_migration, None)


class MigrationDb:
    def __init__(self,
                 db_instance_with_connect,
                 settings_migrations):
        if not isinstance(db_instance_with_connect, DbUtil):
            raise TypeError
        self.db_instance = db_instance_with_connect
        self.settings_migrations = settings_migrations
        self.migrations = Migrations(self.settings_migrations)

    def make_transactions(self):
        if self.check_is_clear_database():
            """
            first work with db we send all existed migrations
            """
            self.set_all_migrations_from_files()
        elif self.is_exist_tables_migration():
            """
            send to db migrations after last migration in db
            """
            self.send_to_db_not_existed_commits()
        elif getattr(self.settings_migrations,
                     'is_drop_existed_tables_in_db_if_dont_exist_migration_table',
                     default=False):
            """
                we clean db and then send all existed transactions 
            """
            self.db_instance.clear_database()
            self.set_all_migrations_from_files()
        else:
            print("We can't change the DB")
            print("Please choose another database")

    def check_is_clear_database(self):
        return self.db_instance.is_clear_database()

    def is_exist_tables_migration(self):
        return self.db_instance.is_exist_table_migrations(getattr(self.settings_migrations,
                                                                  'table_to_save_migrations_store',
                                                                  default=SettingsMigrations.default_settings[
                                                                      'table_to_save_migrations_store']))

    def set_all_migrations_from_files(self):
        started_migration_name = self.migrations.search_schema_where_previous_migration_is(None)
        self.set_to_db_from_migration(started_migration_name)

    def send_to_db_not_existed_commits(self):
        last_migration_in_db = self.db_instance.get_last_migration(self.settings_migrations.table_to_save_migrations_store,
                                                                   self.settings_migrations.current_migration)
        if last_migration_in_db is not None:
            if self.migrations.get_migration_by_name_migration(last_migration_in_db)is not None:
                started_migration = self.migrations.search_schema_where_previous_migration_is(last_migration_in_db)
                self.set_to_db_from_migration(started_migration)
            else:
                if getattr(self.settings_migrations, 'is_roll_back_transactions_to_existed_in_db', False):
                    #search from all migrations last existed migration in files and rollback migrations in db
                    # TODO implement
                    pass
                else:
                    print('Please choice another db or change settings')
        else:
            # empty db commits then insert all migrations
            self.set_all_migrations_from_files()

    def set_to_db_from_migration(self, migration_name):
        while True:
            if migration_name is None:
                break
            migration = self.migrations.get_migration_by_name_migration(migration_name)
            current_migration = MigrationToImplement(**migration)
            is_good, message = self.db_instance.apply_migration(current_migration,
                                                                self.settings_migrations.table_to_save_migrations_store)
            if not is_good:
                raise RuntimeError(message)
            migration_name = self.migrations.search_schema_where_previous_migration_is(migration_name)

        # get this migration and start send to db
        pass

    def get_last_migration(self):
        name_last_migration = self.migrations.get_files_migrations()[-1].split('.')[0]
        last_migration = self.migrations.get_migration_by_name_migration(name_last_migration)
        # print(name_last_migration)
        migr = MigrationToImplement(**last_migration)
        print(migr)
        migr.make_insert_row_migration(self.db_instance)
        print(migr.queries_to_run)
        self.db_instance.save_migrations_data(migr,
                                              self.settings_migrations.table_to_save_migrations_store)


class MigrationToImplement():
    attributes_to_ignore = [
        'attributes_to_ignore',
        'queries_to_run'
    ]

    def __init__(self,
                 previous_migration,
                 current_migration,
                 comment,
                 date,
                 who_make_migration,
                 schema):
        self.previous_migration = previous_migration
        self.current_migration = current_migration
        self.comment = comment
        self.date = date
        self.who_make_migration = who_make_migration
        self.schema = schema
        self.queries_to_run = list()

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
                    add_column = column_tmp.alter_table(name_table, action, db_instance)
                    list_alter_table_add.append(add_column)
            return list_alter_table_add

        def drop_tables(to_drop):
            list_to_drop = list()
            for name_table in to_drop.keys():
                if to_drop[name_table]:
                    # drop columns
                    for column_name, column_data in to_drop[name_table].items():
                        column_tmp = ColumnSchema(**column_data)
                        add_column = column_tmp.alter_table(name_table, 'drop', db_instance)
                        list_to_drop.append(add_column)
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



if __name__ == '__main__':
    # print(Migration.get_name())
    mig = Migration(None)
    print(mig.empty())
