from migrant.model.schema import Schema

# def insert():
#     pass


class CRUD(object):
    def execute(self, db_instance):
        raise NotImplementedError

    def where(self):
        pass

    def group_by(self):
        pass

    def to_str_select(self):
        return ''


class Insert(CRUD):
    def __init__(self, value_to_insert):
        # if isinstance(value_to_insert, list):
        #     for val in value_to_insert:
        #         if not isinstance(val, Schema):
        #             raise TypeError('Incorrect type for insert to db')
        #     self.value_to_insert = value_to_insert
        if isinstance(value_to_insert, Schema):
            self.value_to_insert = [value_to_insert]
        else:
            raise TypeError('Incorrect type for insert to db')

    def execute(self, db_instance, **kwargs):
        for table_to_insert in self.value_to_insert:
            table = table_to_insert.get_table()
            select_insert = table.insert_row_table(returning_values=kwargs.get('returning_values', list()))
            db_instance.make_cud_request(select_insert)
