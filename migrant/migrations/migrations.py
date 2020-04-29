import os
import traceback

from migrant._utils.helper import download_json
from migrant.connect.db_adaptation.db_util import DbUtil
from .migration import MigrationToImplement


class FileStoryMigrations:
    """
    class for work with saved migrations
    """

    def __init__(self, settings_project):
        self.settings_project = settings_project
        self.migrations = dict()
        self.download_all_migrations()

    def get_files_migrations(self):
        try:
            files_migration = os.listdir(self.settings_project.folder_migrations)
        except:
            traceback.print_exc()
            files_migration = list()

        return files_migration

    def download_all_migrations(self):
        for file in self.get_files_migrations():
            tmp_dict = download_json(os.path.join(self.settings_project.folder_migrations, file))
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

    def get_lat_migration(self):
        current_migration = self.search_schema_where_previous_migration_is(None)
        while True:
            tmp_migration = self.get_migration_by_name_migration(current_migration)
            if tmp_migration is None:
                break
            previous = self.search_schema_where_previous_migration_is(current_migration)
            if previous is None:
                break
            current_migration = previous
        return current_migration

    def get_migrations_after_migration(self, migration_name):
        result = list()
        current_migration = self.search_schema_where_previous_migration_is(migration_name)
        while True:
            tmp_migration = self.get_migration_by_name_migration(current_migration)
            if tmp_migration is None:
                break
            result.append(tmp_migration)
            previous = self.search_schema_where_previous_migration_is(current_migration)
            if previous is None:
                break
            current_migration = previous
        return result


class MigrationsApplyToDb:
    """
    class for apply not applied migrations to db

    """

    def __init__(self,
                 db_instance_with_connect,
                 settings_project):
        if not isinstance(db_instance_with_connect, DbUtil):
            raise TypeError
        self.db_instance = db_instance_with_connect
        self.settings_project = settings_project
        self.migrations = FileStoryMigrations(self.settings_project)

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
        elif getattr(self.settings_project.settings_migrations,
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
        return self.db_instance.is_exist_table_migrations(getattr(self.settings_project.settings_migrations,
                                                                  'table_to_save_migrations_store',
                                                                  ))

    def set_all_migrations_from_files(self):
        started_migration_name = self.migrations.search_schema_where_previous_migration_is(None)
        self.set_to_db_from_migration(started_migration_name)

    def send_to_db_not_existed_commits(self):
        last_migration_in_db = self.db_instance.get_last_migration(
            self.settings_project.settings_migrations.table_to_save_migrations_store,
            self.settings_project.settings_migrations.name_key_column)
        if last_migration_in_db is not None:
            if self.migrations.get_migration_by_name_migration(last_migration_in_db) is not None:
                started_migration = self.migrations.search_schema_where_previous_migration_is(last_migration_in_db)
                self.set_to_db_from_migration(started_migration)
            else:
                print('database transaction status exceeds storage transaction state ')
                print('input "y" if you want drop db and remake new ')
                val = input()
                if val.lower() in ['y', 'yes']:
                    print('start clean db')
                    self.db_instance.clear_database()
                    self.set_all_migrations_from_files()
                else:
                    return
                # if getattr(self.settings_project.settings_migrations, 'is_roll_back_transactions_to_existed_in_db',
                #            False):
                #     # search from all migrations last existed migration in files and rollback migrations in db
                #     # TODO implement
                #     pass
                # else:
                #     print('Please choice another db or change settings')
        else:
            # empty db commits then insert all migrations
            self.set_all_migrations_from_files()

    def set_to_db_from_migration(self, migration_name):
        while True:
            if migration_name is None:
                break
            migration = self.migrations.get_migration_by_name_migration(migration_name)
            migration['settings_migrations'] = self.settings_project.settings_migrations
            current_migration = MigrationToImplement(**migration)
            is_good, message = self.db_instance.apply_migration(current_migration,
                                                                self.settings_project.settings_migrations.table_to_save_migrations_store)
            if not is_good:
                raise RuntimeError(message)
            migration_name = self.migrations.search_schema_where_previous_migration_is(migration_name)

        # get this migration and start send to db
        pass

    def get_last_migration(self):
        name_last_migration = self.migrations.get_files_migrations()[-1].split('.')[0]
        last_migration = self.migrations.get_migration_by_name_migration(name_last_migration)
        # print(name_last_migration)
        last_migration['settings_migrations'] = self.settings_project.settings_migrations
        migr = MigrationToImplement(**last_migration)
        migr.make_insert_row_migration(self.db_instance)
        self.db_instance.save_migrations_data(migr,
                                              self.settings_project.settings_migrations.table_to_save_migrations_store)

    def get_migrations_after_migration(self, last_migration_in_storage):
        pass

    def is_exist_migration_in_db(self, name_migration):
        return self.db_instance.is_exist_migration_in_db(name_migration,
                                                         self.settings_project.settings_migrations.table_to_save_migrations_store,
                                                         self.settings_project.settings_migrations.name_key_column)


class StatusMigrations:
    def __init__(self, settings_project, db_instance):
        self.settings_project = settings_project
        self.db_instance = db_instance
        self.files_migrations = FileStoryMigrations(self.settings_project)
        self.db_migrations = MigrationsApplyToDb(self.db_instance, self.settings_project)

    def get_last_storage_migration(self):
        return self.files_migrations.get_lat_migration()

    def get_last_db_migration(self):
        last_migration_in_db = self.db_instance.get_last_migration(
            self.settings_project.settings_migrations.table_to_save_migrations_store,
            self.settings_project.settings_migrations.name_key_column)
        return last_migration_in_db

    def diff_storage_and_db(self, last_migration_in_db, last_migration_in_storage):
        is_exist_db_in_storage_migration = self.files_migrations.migrations.get(last_migration_in_db, None)
        if is_exist_db_in_storage_migration:
            print('Migrations in the storage are older than the migrations in the database ')
            print('Last migration in storage:', last_migration_in_storage)
            print('Last migration in db:', last_migration_in_db)
            res = self.files_migrations.get_migrations_after_migration(last_migration_in_db)
            print('Uncommitted next migration(s)')
            for migration in res:
                print(migration["current_migration"])
            print('Use command "migrate" to fix problem')
        else:
            if self.db_migrations.is_exist_migration_in_db(last_migration_in_storage):
                print('You can use "migrate" with settings "is_roll_back_transactions_to_existed_in_db" True '
                      'for fix this problem')
            else:
                print('Migration {last_migration_in_storage} not exist in DB '.format(
                    last_migration_in_storage=last_migration_in_storage))
                print("You can use command 'migrate' with settings migrations "
                      "'is_drop_then_create_new_for_update_column_table' True")
