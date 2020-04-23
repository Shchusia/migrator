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

    @staticmethod
    def get_str_for_primary(list_primary_keys):
        is_add_in_table = True
        str_return = "PRIMARY KEY ( {})".format(' ,'.join([str(p_k) for p_k in list_primary_keys]))
        return str_return, is_add_in_table


class PostgresUtil(DbUtil):
    default_settings_connect = {
        'dbname': 'postgres',
        'user': 'postgres',
        'host': 'localhost',
        'password': '',
        'port': '5432',
    }
    conformity = PostgresConformity()
    connect = None

    def __init__(self, str_connect=None, **kwargs):

        if str_connect is not None:
            self.str_connect_to_db = str_connect
        else:
            str_connect_to_db = ''
            for option in self.default_settings_connect:
                str_connect_to_db += "{}='{}' ".format(option,
                                                       kwargs.get(option,
                                                                  self.default_settings_connect[option]))
            self.str_connect_to_db = str_connect_to_db

        self.connect = self._connect()

    def _connect(self):
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

    def save_migrations_data(self, migration):
        raise NotImplementedError

    def drop_table(self):
        raise NotImplementedError

    def get_last_migration(self):
        raise NotImplementedError

    def is_clear_database(self):
        select = '''
            SELECT *
            FROM pg_catalog.pg_tables
            WHERE schemaname != 'pg_catalog'
            AND schemaname != 'information_schema';
        '''
        res = self.make_select_request(select)
        table_names = [
            table_name[1]
            for table_name in res
        ]
        return len(table_names) == 0

    def is_exist_table_migrations(self,
                                  name_table):
        select = '''
            SELECT EXISTS (
                SELECT 1
                FROM   information_schema.tables
                WHERE  table_schema = 'public'
                AND    table_name = '{}');
        '''.format(name_table)
        result = self.make_select_request(select)
        return result[0][0]

    def clear_database(self):
        selects_to_run = [
            'DROP SCHEMA public CASCADE;',
            'CREATE SCHEMA public;',
            'GRANT ALL ON SCHEMA public TO postgres;',
            'GRANT ALL ON SCHEMA public TO public;'
        ]
        for select in selects_to_run:
            self.make_cud_request(select)

