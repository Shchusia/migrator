from _types.mig_types import MigType
from _utils.helper import get_class_name, check_2_dicts
import traceback


class Model(object):

    def make_schema(self, ):
        raise NotImplementedError

    def make_row(self, db_instance):
        raise NotImplementedError


class Reference(Model):
    # TODO make match
    def __init__(self,
                 ref_to_table,
                 ref_to_column_table,
                 on_delete=None,
                 on_update=None,
                 **kwargs):
        self.table = ref_to_table
        self.column = ref_to_column_table
        self.on_delete = on_delete
        self.on_update = on_update
        self.table_name = ''
        self.column_name = ''

    def to_string(self):
        if isinstance(self.table, str):
            self.table_name = self.table
        else:
            self.table_name = get_class_name(self.table)
        if isinstance(self.column, str):
            self.column_name = self.column
        else:
            self.column_name = self.column.column_name

    def make_schema(self):
        self.to_string()
        return {
            'ref_to_table': self.table_name,
            'ref_to_column_table': self.column_name,
            'on_delete': self.on_delete,
            'on_update': self.on_update
        }

    def make_row(self,
                 db_instance):
        def make_on_action_data(action, action_value):
            append_row = ''
            try:
                if hasattr(db_instance.conformity, action):
                    cur_object = getattr(db_instance.conformity, action)
                    name_attr = list(filter(lambda x: x[1] != '_', dir(cur_object)))
                    converted = {getattr(cur_object, val).lower(): val for val in name_attr}
                    if converted.get(action_value.lower(), None) is None:
                        raise ValueError(
                            "Class {} don't have command for {}".format(
                                getattr(db_instance.conformity, action).__name__,
                                action_value))
                    else:
                        append_row += ' ' + ' '.join(action.split('_')) + ' ' + getattr(
                            getattr(db_instance.conformity, action),
                            converted[action_value.lower()])
                else:
                    raise ValueError(
                        "Class {} don't have attribute {} you couldn't use {} attribute".format(
                            db_instance.conformity.__name__, action,
                            action.lower()))
            except:
                traceback.print_exc()
            return append_row

        self.to_string()
        row = ' REFERENCES {} ({})'.format(self.table_name, self.column_name)
        if self.on_delete:
            row += make_on_action_data('ON_DELETE', self.on_delete)
        if self.on_update:
            row += make_on_action_data('ON_UPDATE', self.on_update)
        return row

    @staticmethod
    def check_correct_references_in_schema(schema_for_check):
        """
        {table: column: ['reference' ]
        :param schema_for_check:
        :return:
        """

        def get_references_in_schema(schema):
            list_references = list()
            for table in schema.keys():
                table_info = schema[table]
                for column in table_info.keys():
                    if table_info[column].get('reference', None) is not None:
                        tmp_dict = {
                            'table': table,
                            'column': column,
                            'column_information': table_info[column]
                        }
                        list_references.append(tmp_dict)
            return list_references

        def check_link_parameters(reference, schema):
            is_correct_cur = True
            message_cur = ''
            to_table_link = reference['column_information']['reference']['ref_to_table']
            to_column_link = reference['column_information']['reference']['ref_to_column_table']
            if schema.get(to_table_link, None) is not None:
                if schema[to_table_link].get(to_column_link, None) is not None:
                    type_column_link = reference['column_information']['column_type']
                    type_column_link_eo = reference['column_information']['type_extra_options']
                    to_type_column = schema[to_table_link][to_column_link]['column_type']
                    to_type_column_eo = schema[to_table_link][to_column_link]['type_extra_options']
                    if type_column_link == to_type_column:
                        res_checker = check_2_dicts(to_type_column_eo, type_column_link_eo)
                        if res_checker:
                            is_correct_cur = False
                            message_cur = res_checker
                        else:
                            pass
                    else:
                        is_correct_cur = False
                        message_cur = """Incorrect reference type '{}.{}.{}' and '{}.{}.{}'""".format(to_column_link,
                                                                                                      to_table_link,
                                                                                                      to_type_column,
                                                                                                      reference[
                                                                                                          'table'],
                                                                                                      reference[
                                                                                                          'column'],
                                                                                                      type_column_link)
                else:
                    is_correct_cur = False
                    message_cur = """ '{}' column in '{}' table does not exist referenced by '{}.{}'""".format(
                        to_column_link,
                        to_table_link,
                        reference['table'],
                        reference['column'])

            else:
                is_correct_cur = False
                message_cur = """The '{}' table referenced by '{}.{}' does not exist  """ \
                    .format(to_table_link,
                            reference['table'],
                            reference['column']
                            )

            return is_correct_cur, message_cur

        list_ref = get_references_in_schema(schema_for_check)
        global_is_correct = True
        global_message = ''
        for ref in list_ref:
            is_correct, message = check_link_parameters(ref, schema_for_check)
            global_is_correct &= is_correct
            global_message += message + ' | '
        if global_is_correct:
            return

        raise AttributeError(global_message)


class Column(Model):
    def __init__(self,
                 column_type=None,
                 is_not_null=False,
                 check=None,
                 default=None,
                 unique=False,
                 primary_key=False,
                 reference=None,
                 column_name='',
                 additional_str_parameter=None,
                 **kwargs
                 ):
        if isinstance(column_type, str):
            subclasses = {cls.__name__: cls for cls in MigType.__subclasses__()}
            if subclasses.get(column_type, None) is None:
                raise ValueError("Subclasses MigType not have class {}".format(column_type))
            else:
                if kwargs.get('type_extra_options', None) is not None:
                    self.column = subclasses[column_type](**kwargs['type_extra_options'])
                else:
                    self.column = subclasses[column_type]()
        elif isinstance(column_type, type):
            print('type')

            if not isinstance(column_type(), MigType):
                raise TypeError('Not correct column type for column table. must realize class MitType')
            self.column = column_type()

        else:
            if not isinstance(column_type, MigType):
                raise TypeError('Not correct column type for column table. must realize class MitType')

            self.column = column_type

        self.is_not_null = is_not_null
        self.default = default
        self.unique = unique
        self.primary_key = primary_key
        if reference is not None:
            if isinstance(reference, Reference):
                self.reference = reference
            else:
                self.reference = Reference(**reference)
        else:
            self.reference = reference
        self.check = check
        self.column_name = column_name
        self.additional_str_parameter = additional_str_parameter
        if not isinstance(self.additional_str_parameter, str):
            self.additional_str_parameter = None

    def __str__(self):
        return '<Column: {}:{}>'.format(self.column_name, self.column.get_type())

    def set_column_name(self,
                        name_atr):
        self.column_name = name_atr

    # def to_string(self):
    #     pass

    def make_schema(self,
                    with_name_column=False,
                    with_object=True):
        column_dict = {
            'column_name': self.column_name,
            'column_type': self.column.get_type(),
            'type_extra_options': self.column.get_extra_options()
        }
        if with_object:
            column_dict['column_object'] = self
        if self.default:
            column_dict['default'] = self.default
        if self.is_not_null:
            column_dict['is_not_null'] = self.is_not_null
        if self.unique:
            column_dict['unique'] = self.unique
        if self.primary_key:
            column_dict['primary_key'] = self.primary_key
        if self.reference:
            column_dict['reference'] = self.reference.make_schema()
        if self.check:
            column_dict['check'] = self.check
        if self.additional_str_parameter:
            column_dict['additional_str_parameter'] = self.additional_str_parameter
        if with_name_column:
            return {
                self.column_name: column_dict
            }
        return column_dict

    def make_row(self, db_instance, is_add_primary_key=True):
        """

        :param db_instance:
        :param is_add_primary_key: parameter for tables where many primary keys
        :return:
        """
        column = '{} {}'.format(self.column_name, self.column.get_db_equivalent(db_instance))
        if self.is_not_null:
            column += ' NOT NULL'
        if self.check:
            column += 'CHECK ( {} )'.format(self.check)
        if self.default:
            column += ' DEFAULT {}'.format(self.default)
        if self.unique:
            column += ' UNIQUE'
        if self.primary_key and is_add_primary_key:
            column += ' PRIMARY KEY'
        if self.additional_str_parameter:
            column += ' {}'.format(self.additional_str_parameter)
        if self.reference:
            column += self.reference.make_row(db_instance)
        return column

    def to_migrate_structure(self,
                             db_instance):
        # print(self.column_type.get_db_equivalent(db_instance))
        if self.references:
            print('reference')
            print(self.references.make_row(db_instance))

    def get_column_name(self):
        return self.column_name


class Table:
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
        print(type(column))
        index_col = self._get_id_column_by_column_name(column.get_column_name())
        if index_col == -1:
            raise ResourceWarning('{} is not exist for drop from table <>'.format(str(column),
                                                                                  self.table_name))
        else:
            del self.columns[index_col]

    def make_create_table_select_table(self, db_instance):
        def get_primary_keys_in_table(colu_s):
            list_p_k = list()
            for col in colu_s:
                if col.primary_key:
                    list_p_k.append(col.column_name)
            return list_p_k

        print(self.table_name)
        list_columns_primary_key = get_primary_keys_in_table(self.columns)
        is_add_p_k = False if len(list_columns_primary_key) > 1 else True
        str_columns_list = [column.make_row(db_instance, is_add_p_k) for column in self.columns]
        table = '''
            CREATE TABLE IF NOT EXIST {}(
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


class ColumnSchema(Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TableSchema(Table):
    def __init__(self, table_name, columns_info):
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
            print(columns_info)
            self.drop_column(ColumnSchema(**columns_info[column]))




if __name__ == '__main__':
    from mig import PostgresUtil
    from te.settings import str_connect_to_db

    db = PostgresUtil(str_connect_to_db)
    ddict = {"create": {
        "user": {
            "id": {
                "column_name": "id",
                "column_type": "Int",
                "type_extra_options": {},
                "primary_key": True
            },
            "name": {
                "column_name": "name",
                "column_type": "Varchar",
                "type_extra_options": {
                    "len_string": 5
                }
            }
        },
        "userinfo": {
            "address": {
                "column_name": "address",
                "column_type": "Text",
                "type_extra_options": {}
            },
            "ref_user": {
                "column_name": "ref_user",
                "column_type": "Int",
                "type_extra_options": {},
                "reference": {
                    "ref_to_table": "user",
                    "ref_to_column_table": "id",
                    "on_delete": "cascade",
                    "on_update": "SET NULL"
                }
            }
        },
        "user_additional_info": {
            "ref_user": {
                "column_name": "ref_user",
                "column_type": "Int",
                "type_extra_options": {},
                "reference": {
                    "ref_to_table": "user",
                    "ref_to_column_table": "id",
                    "on_delete": "cascade",
                    "on_update": None
                }
            }
        }
    }
    }

    for table, columns in ddict["create"].items():
        ts = TableSchema(table, columns)
        select = ts.make_create_table_select_table(db)
        print(select)
