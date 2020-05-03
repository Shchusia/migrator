import traceback

from migrant.connect.db_adaptation.db_util import DbUtil


class Connect(object):
    _dict_db_instance = {
        # Postgres
        'postgresql': 'postgresql',
        'postgresql+psycopg2': 'postgresql',  # 'postgresql+psycopg2://scott:tiger@localhost/mydatabase'
        'postgresql+pg8000': 'postgresql',  # 'postgresql+pg8000://scott:tiger@localhost/mydatabase'
        # MySql # TODO
        'mysql': 'mysql',  # 'mysql://scott:tiger@localhost/foo'
        'mysql+mysqldb': 'mysql',  # 'mysql+mysqldb://scott:tiger@localhost/foo'
        'mysql+pymysql': 'mysql',  # 'mysql+pymysql://scott:tiger@localhost/foo'
        # Oracle # TODO
        'oracle': 'oracle',  # 'oracle://scott:tiger@127.0.0.1:1521/sidname'
        'oracle+cx_oracle': 'oracle',  # 'oracle+cx_oracle://scott:tiger@tnsname'
        # Microsoft SQL Server # TODO
        'mssql+pyodbc': 'mssql',  # 'mssql+pyodbc://scott:tiger@mydsn'
        'mssql+pymssql': 'mssql',  # 'mssql+pymssql://scott:tiger@hostname:port/dbname'
        # SQLite # TODO
        'sqlite': 'sqlite'  # 'sqlite:///foo.db'
    }

    def __init__(self, str_connect_engine: str):
        """
        Class connect to db
        :param str_connect_engine: str connect for make engine sql_alchemy
        use get_examples for got strings examples
        """
        self.str_connect_to_db = str_connect_engine
        self.type_db_class_dict = DbUtil.get_adaptation_instances_db()
        self.db_instance = self.__get_instance_db_connect()

    def __get_instance_db_connect(self):
        try:
            driver_connect = self.str_connect_to_db.split(':')[0]
            type_db = self._dict_db_instance.get(driver_connect, None)
            assert type_db is not None, 'Not implemented ClassConnect for db: "{}"'.format(driver_connect)
            cls = self.type_db_class_dict.get(type_db, None)
            assert cls is not None, 'Not implemented ClassConnect for db: "{}"'.format(driver_connect)
            if not cls.is_matches_regular_expression_str_connect(self.str_connect_to_db):
                raise ValueError('Invalid str connect. Not matched to correct structure')
            current_instance = cls(engine_str=self.str_connect_to_db)
            return current_instance
        except:
            traceback.print_exc()
            raise ValueError('invalid str for create engine' + 'Look sqlalchemy engine str connect '
                                                               'https://docs.sqlalchemy.org/en/13/core/engines.html')

    def get_instance(self):
        return self.db_instance

    def get_engine(self):
        return self.db_instance.engine

    @classmethod
    def get_examples(cls):
        type_db_class_dict = DbUtil.get_adaptation_instances_db()
        reverse = dict()
        for key, val in cls._dict_db_instance.items():
            tmp = reverse.get(val, list())
            tmp.append(key)
            reverse[val] = tmp

        # print(reverse)

        for sql_name in type_db_class_dict.keys():
            for data in reverse[sql_name]:
                print(data + type_db_class_dict[sql_name].example_str)


if __name__ == '__main__':
    Connect('').get_examples()
