from .settings import Settings
from migrant.connect import Connect
from migrant.connect.db_adaptation.db_util import DbUtil
from migrant.model.schema import SchemaMaker


class Migrate:
    """
    Main class migrate
    """
    def __init__(self,
                 db_connect=None,
                 settings_file='migrate.yaml'):
        """

        :param db_connect:
        :param settings_file:
        """
        self.settings = Settings(settings_file)
        self.settings_project = self.settings.get_settings_project()
        self.settings_migrations = self.settings.get_settings_migrations()

        if db_connect is not None:
            if isinstance(db_connect, Connect):
                self.db_connect = db_connect.get_instance()
            elif isinstance(db_connect, DbUtil):
                self.db_connect = db_connect
            else:
                raise TypeError('db_connect must be extand class DbUtil')
        if db_connect is None and hasattr(self.settings_project, 'last_engine_str'):
            db_connect = Connect(getattr(self.settings_project, 'last_engine_str'))
            self.db_connect = db_connect.get_instance()
        elif db_connect is None:
            pass
        else:
            self.settings.last_engine_str = self.db_connect.make_str_connect_engine()
        self.db_connect = db_connect

        self.schema = SchemaMaker(db_instance=self.db_connect,
                                  settings=self.settings,
                                  is_print_sub_classes=True)


    def create_and_update(self):
        pass




