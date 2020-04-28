import os
import traceback

from migrant._utils.helper import download_json


class FileStoryMigrations:
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
