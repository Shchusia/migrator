from migrant.connect.db_adaptation.db_util import DbUtil, DBConformity
import psycopg2
import json
from migrant.model.mi_types import MigType
import re


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
    JSON = 'JSON'

    #
    ON_DELETE = OnActionPostgres()
    ON_UPDATE = OnActionPostgres()

    @staticmethod
    def get_str_for_primary(list_primary_keys):
        is_add_in_table = True
        str_return = "PRIMARY KEY ( {})".format(' ,'.join([str(p_k) for p_k in list_primary_keys]))
        return str_return, is_add_in_table

    @staticmethod
    def alter_table(name_table, column, alter_action, db, **kwargs):
        ref_column = ''
        select = 'ALTER TABLE IF EXISTS {name_table} '.format(name_table=name_table)
        if alter_action == 'add':
            str_column = PostgresConformity.alter_table_add_column(column, db)
        elif alter_action == 'upgrade':
            str_column, ref_column = PostgresConformity.alter_table_update_column(column, db, name_table, **kwargs)
        else:
            # drop
            str_column = PostgresConformity.alter_table_drop_column(column, db)
        select += str_column + ';'
        selects = list()
        selects.append(select)
        if ref_column:
            select_new = 'ALTER TABLE IF EXISTS {name_table} '.format(name_table=name_table)
            select_new += ref_column + ';'
            selects.append(select_new)
        return selects

    @staticmethod
    def alter_table_add_column(column, db):
        return ' ADD COLUMN ' + column.make_sql_request(db, is_add_primary_key=True)

    @staticmethod
    def alter_table_update_column(column, db, column_table, **kwargs):
        str_column = ''
        ref_column = ''
        if kwargs.get('is_recreate_column_to_update'):
            str_column = ' DROP COLUMN IF EXISTS ' + column.column_name + ' CASCADE ' + ','
            str_column += ' ADD COLUMN ' + column.make_sql_request(db, is_add_primary_key=True)
            return str_column, ref_column

        str_column += 'ALTER COLUMN  {column_name} SET DATA TYPE {type_column}'.format(column_name=column.column_name,
                                                                                       type_column=column.get_column_type())
        if column.is_not_null:
            str_column += ', ALTER COLUMN  {column_name} SET NOT NULL'.format(column_name=column.column_name, )
        if column.check:
            str_column += ', ADD CONSTRAINT {column_name} CHECK ({check})'.format(column_name=column.column_name,
                                                                                  check=column.check)
        if column.default:
            str_column += ', ALTER COLUMN  {column_name} SET DEFAULT {default}'.format(column_name=column.column_name,
                                                                                       default=column.default)
        if column.unique:
            str_column += ', ADD CONSTRAINT {column_name} UNIQUE'.format(column_name=column.column_name)
        if column.primary_key:
            str_column += ', ADD PRIMARY KEY ({column_name})'.format(column_name=column.column_name)
        # if self.additional_str_parameter:
        #     column += ' {}'.format(self.additional_str_parameter)
        if column.reference:
            ref_column += 'ADD CONSTRAINT {name_table}_{column_name}_fkey FOREIGN KEY ({column_name}) {sql_ref}'.format(
                column_name=column.column_name,
                name_table=column_table,
                sql_ref=column.reference.make_sql_request(db))
        return str_column, ref_column

    @staticmethod
    def alter_table_drop_column(column, db):
        return ' DROP COLUMN IF EXISTS ' + column.column_name + ' CASCADE'


class PostgresUtil(DbUtil):
    sql_name = 'postgresql'

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
            if kwargs.get('engine_str', None) is not None:
                self.make_connect_from_engine_str(kwargs['engine_str'])
            else:
                self.make_str_connect_from_dict(**kwargs)

        self.connect = self._connect()

    def __str__(self):
        return "<Postgres: {}>".format(self.make_str_connect_engine())

    def make_str_connect_from_dict(self, **kwargs):
        str_connect_to_db = ''
        for option in self.default_settings_connect:
            str_connect_to_db += "{}='{}' ".format(option,
                                                   kwargs.get(option,
                                                              self.default_settings_connect[option]))
        self.str_connect_to_db = str_connect_to_db

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

    @staticmethod
    def is_matches_regular_expression_str_connect(str_connect):
        regex = r"([\w]+(\+[\w]+)*)://[\w]+:[\w]+@([\w]+(:[\d]+)*)/[\w]+"
        res = re.match(regex, str_connect)
        return res is not None

    def make_connect_from_engine_str(self,
                                     str_connect):
        """

        'postgresql': 'postgres',  # 'postgresql://scott:tiger@localhost:5430/mydatabase'
        'postgresql+psycopg2': 'postgres',  # 'postgresql+psycopg2://scott:tiger@localhost/mydatabase'
        'postgresql+pg8000': 'postgres',  # 'postgresql+pg8000://scott:tiger@localhost/mydatabase'

        :param str_connect:
        :return:
        """
        without_type_db = str_connect.split('://')[1]
        user_password, other = without_type_db.split('@')
        user, password = user_password.split(':') if ':' in user_password else (user_password, '')
        host_port, data_base = other.split('/')
        host, port = host_port.split(':') if ':' in host_port else (host_port, self.default_settings_connect['port'])
        self.default_settings_connect['dbname'] = data_base
        self.default_settings_connect['user'] = user
        self.default_settings_connect['host'] = host
        self.default_settings_connect['password'] = password
        self.default_settings_connect['port'] = port
        self.make_str_connect_from_dict()
        # self._connect()
        self.make_engine(str_connect)

    def make_str_connect_engine(self):
        data = self.str_connect_to_db.split()
        _dict_ = {
            key.split('=')[0]: key.split('=')[1].replace("'", '')
            for key in data
        }
        _dict_['sql_name'] = self.sql_name
        val = '{sql_name}://{user}:{password}@{host}:{port}/{dbname}'.format(**_dict_)
        return val

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
                rows_migration_table.append('{} Text'.format(column))
                continue
            for _type in list_to_check:
                if isinstance(data, _type):
                    rows_migration_table.append('{} {}'.format(column,
                                                               dict_types_python_db[_type]))
                    break
            else:
                rows_migration_table.append('{} Text'.format(column))
        create_select += '({});'.format(','.join(rows_migration_table))
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

    def is_exist_migration_in_db(self, name_migration, name_table, name_column,):
        select = '''
                     SELECT {name_column}
                     FROM {name_table}
                     WHERE _id = (
                        SELECT max(_id)
                        FROM {name_table}
                        WHERE {name_column} = '{name_migration}'
)
                '''.format(name_column=name_column,
                           name_table=name_table,
                           name_migration=name_migration)
        res = self.make_select_request(select)
        return True if res else False


class Json(MigType):
    def db_equivalent(self, db_type):
        return db_type.conformity.JSON


