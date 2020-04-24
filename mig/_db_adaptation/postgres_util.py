from .db_util import DbUtil,DBConformity
import psycopg2
import json

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

    def save_migrations_data(self,
                             migration,
                             table_migration):
        if not self.is_exist_table_migrations(name_table=table_migration):
            self.create_migrations_table(table_migration, migration)
        data_to_save = migration.get_data_to_save_in_db()
        select = 'INSERT INTO {} '.format(table_migration)
        columns = list()
        values = list()
        for col, val in data_to_save.items():
            columns.append(col)
            if isinstance(val, dict):
                values.append("'{}'".format(json.dumps(val)))
            elif isinstance(val, str):
                values.append("'{}'".format(val))
            elif val is None:
                values.append('Null')
            else:
                values.append(str(val))
        select += '({}) VALUES ({});'.format(','.join(columns), ','.join(values))
        print(select)
        self.make_cud_request(select)

    def drop_table(self):
        raise NotImplementedError

    def get_last_migration(self,
                           name_table,
                           name_column):
        select = '''
            select {name_column}
            FROM {name_table}
            WHERE _id = ( 
                SELECT max(_id)
                FROM {name_table})
        '''.format(name_column=name_column,
                   name_table=name_table)
        try:
            name_migration = self.make_select_request(select)[0][0]
        except:
            name_migration = None
        return name_migration

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

    def clear_database(self):
        selects_to_run = [
            'DROP SCHEMA public CASCADE;',
            'CREATE SCHEMA public;',
            'GRANT ALL ON SCHEMA public TO postgres;',
            'GRANT ALL ON SCHEMA public TO public;'
        ]
        for select in selects_to_run:
            self.make_cud_request(select)

    def create_migrations_table(self,
                                name_table,
                                migration):
        dict_types_python_db = {
            int: 'Integer',
            dict: 'JSON',
            bool: 'Boolean',
            str: 'Text',
        }
        list_to_check = [int, dict, bool, str]
        is_add_id = True
        create_select = '''
            CREATE TABLE IF NOT EXISTS {}
        '''.format(name_table)
        rows_migration_table = list()
        if is_add_id:
            rows_migration_table.append('_id SERIAL PRIMARY KEY')
        data_to_save = migration.get_data_to_save_in_db()
        for column, data in data_to_save.items():
            if data is None:
                rows_migration_table. append('{} Text'.format(column))
                continue
            for _type in list_to_check:
                if isinstance(data, _type):
                    rows_migration_table.append('{} {}'.format(column,
                                                               dict_types_python_db[_type]))
                    break
            else:
                rows_migration_table. append('{} Text'.format(column))
        create_select += '({});'.format(','.join(rows_migration_table))
        print(create_select)
        self.make_cud_request(create_select)

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

    def apply_migration(self,
                        migration,
                        table_migration):
        list_queries = migration.get_queries(self)
        is_good, message = True, ''
        try:
            cur = self.connect.cursor()
            for query in list_queries:
                cur.execute(query)
            self.save_migrations_data(migration,
                                      table_migration)
            self.connect.commit()

        except Exception as e:
            self.connect.rollback()
            is_good = False
            message = str(e)
        finally:
            pass

        return is_good, message


