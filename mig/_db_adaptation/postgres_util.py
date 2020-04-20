from .db_util import DbUtil,DBConformity
import psycopg2


class OnActionPostgres:
    NO_ACTION = 'NO ACTION'
    RESTRICT = 'RESTRICT'
    CASCADE = 'CASCADE'
    SET_NULL = 'SET NULL'
    SET_DEFAULT = 'SET DEFAULT'


class PostgresConformity(DBConformity):
    TEXT_TYPE = 'TEXT'
    VARCHAR_TYPE = 'VARCHAR'
    CHAR_TYPE = 'CHAR'

    #
    ON_DELETE = OnActionPostgres()
    ON_UPDATE = OnActionPostgres()


class PostgresUtil(DbUtil):
    default_settings_connect = {
        'dbname': 'postgres',
        'user': 'postgres',
        'host': 'localhost',
        'password': '',
        'port': '5432',
    }
    conformity = PostgresConformity()

    def __init__(self, str_connect=None, **kwargs):

        if str_connect is not None:
            self.str_connect_to_db = str_connect
        else:
            str_connect_to_db = ''
            for option in self.default_settings_connect:
                str_connect_to_db += "{}='{}' ".format(option,
                                                       kwargs.get(option,
                                                                  self.default_settings_connect[option]))
            self.sstr_connect_to_db = str_connect_to_db

        self.connect = self._connect()

    def _connect(self):
        conn = None
        try:
            conn = psycopg2.connect(self.str_connect_to_db)
        except Exception as e:
            # traceback.print_exc()
            print("I am unable to connect to the database postgres")
            raise ConnectionError("don't connect to db" + str(e))
        return conn

    def _disconnect(self):
        try:
            self.connect.close()
        except:
            pass




