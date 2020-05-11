from migrant.model.model import Model
from .column import ColumnSchema


class Table(Model):
    def __init__(self, table_name=None):
        self.table_name = table_name
        self.columns = list()

    def __str__(self):
        return '<Table: {} columns: {} >'.format(self.table_name, ','.join([str(column) for column in self.columns]))

    def _get_id_column_by_column_name(self,
                                      column_name):
        index_column = -1
        for i, col in enumerate(self.columns):
            if col.get_column_name() == column_name:
                index_column = i
                break
        return index_column

    def append_column(self,
                      column):
        self.columns.append(column)

    def upgrade_column(self,
                       column):
        index_col = self._get_id_column_by_column_name(column.get_column_name())
        if index_col == -1:
            raise ResourceWarning('{} is not exist for update in table <>'.format(str(column),
                                                                                  self.table_name))
        else:
            self.columns[index_col] = column

    def drop_column(self,
                    column):
        # print(type(column))
        index_col = self._get_id_column_by_column_name(column.get_column_name())
        if index_col == -1:
            raise ResourceWarning('{} is not exist for drop from table <>'.format(str(column),
                                                                                  self.table_name))
        else:
            del self.columns[index_col]

    def make_create_table_request(self,
                                  db_instance):
        def get_primary_keys_in_table(colu_s):
            list_p_k = list()
            for col in colu_s:
                if col.primary_key:
                    list_p_k.append(col.column_name)
            return list_p_k

        list_columns_primary_key = get_primary_keys_in_table(self.columns)
        is_add_p_k = False if len(list_columns_primary_key) > 1 else True
        str_columns_list = [column.make_sql_request(db_instance, is_add_p_k) for column in self.columns]
        table = '''
            CREATE TABLE {}(
            {}
        '''.format(self.table_name, ','.join(str_columns_list))
        if not is_add_p_k:
            str_add, is_add_in_table = db_instance.conformity.get_str_for_primary(list_columns_primary_key)
            if is_add_in_table:
                table += str_add + ');'
            else:
                table += ');' + str_add + ';'
        else:
            table += ');'
        return table

    def get_columns_dict(self):
        return {
            column.get_column_name(): column for column in self.columns
        }

    def compare_with_table(self, other):
        if not isinstance(other, Table):
            raise ValueError('{} is not instance Table class'.format(str(other)))

        self_column_dict = self.get_columns_dict()
        other_column_dict = other.get_columns_dict()
        new_columns = set(self_column_dict.keys()) - set(other_column_dict.keys())
        deleted_columns = set(other_column_dict.keys()) - set(self_column_dict.keys())
        upgraded_columns = list()
        intersection_columns = set(self_column_dict.keys()) & set(other_column_dict.keys())
        for column in intersection_columns:
            if other_column_dict[column] == self_column_dict[column]:
                continue
            else:
                upgraded_columns.append(column)
        add_col = {col: self_column_dict[col] for col in new_columns}
        drop_col = {col: other_column_dict[col] for col in deleted_columns}
        up_col = {col: self_column_dict[col] for col in upgraded_columns}
        dict_result = {
            'add': add_col,
            'upgrade': up_col,
            'drop': drop_col
        }
        return dict_result

    def make_schema(self,
                    with_name_column=False,
                    with_object=True):
        schema_table = dict()
        for column in self.columns:
            schema_table[column.get_column_name()] = column.make_schema(with_name_column=False,
                                                                        with_object=with_object)
        if with_object:
            schema_table['object'] = self
        if with_name_column:
            return {
                self.table_name: schema_table
            }
        return schema_table

    def make_sql_request(self,
                         db_instance):
        return self.make_create_table_request(db_instance)

    def drop_this_table(self):
        return self.drop_table(self.table_name)

    @staticmethod
    def drop_table(table_name):
        return 'DROP TABLE IF EXISTS {} CASCADE'.format(table_name)

    def insert_row_table(self,
                         returning_values=list()):
        select = 'INSERT INTO {table_name}'.format(table_name=self.table_name)
        column_name = list()
        column_value = list()
        for column in self.columns:
            if not column.is_correct_value():
                raise ValueError('Incorrect values to insert')
            column_name.append(column.get_column_name())
            column_value.append(column.value_to_insert())
        select += '({columns}) VALUES ({values})'.format(columns=','.join(column_name),
                                                         values=','.join(column_value))
        if returning_values:
            select += 'RETURNING {ret_col}'.format(ret_col=','.join(returning_values))
        return select


class TableSchema(Table):
    def __init__(self,
                 table_name,
                 columns_info):
        super().__init__(table_name)
        for column in columns_info.keys():
            self.append_column(ColumnSchema(**columns_info[column]))

    def append_columns(self, columns_info):
        for column in columns_info.keys():
            self.append_column(ColumnSchema(**columns_info[column]))

    def upgrade_columns(self, columns_info):
        for column in columns_info.keys():
            self.upgrade_column(ColumnSchema(**columns_info[column]))

    def drop_columns(self, columns_info):
        for column in columns_info.keys():
            self.drop_column(ColumnSchema(**columns_info[column]))
