import psycopg2


class Connect(object):
    def __init__(self, str_connect):
        self.str_connect_to_db = str_connect

    def _connect(self):
        conn = None
        try:
            conn = psycopg2.connect(self.str_connect_to_db)
        except Exception as e:
            # traceback.print_exc()
            print("I am unable to _connect to the database postgres")
            raise ConnectionError("don't _connect to db" + str(e))
        return conn





