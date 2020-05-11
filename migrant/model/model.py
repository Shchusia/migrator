import traceback

from migrant._utils.helper import get_class_name, check_2_dicts
from migrant.mi_types.mi_types import MigType


# from sqlalchemy import Column as ColumnAlchemy


class Model(object):

    def make_schema(self,
                    with_name_column=False,
                    with_object=True):
        raise NotImplementedError

    def make_sql_request(self, db_instance):
        raise NotImplementedError






if __name__ == '__main__':
    pass
