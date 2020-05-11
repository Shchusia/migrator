import traceback

from migrant._utils.helper import get_class_name, check_2_dicts
from migrant.model.model import Model


class Reference(Model):
    # TODO make match
    def __init__(self,
                 ref_to_table,
                 ref_to_column_table,
                 on_delete=None,
                 on_update=None,
                 **kwargs):
        self.table = ref_to_table
        # print(self.table)
        self.column = ref_to_column_table
        self.on_delete = on_delete
        self.on_update = on_update
        self.table_name = ''
        self.column_name = ''
        #

    def to_string(self):
        if isinstance(self.table, str):
            self.table_name = self.table
        else:
            self.table_name = get_class_name(self.table)
        # print(type(self.column))

        if isinstance(self.column, str):
            self.column_name = self.column
        else:
            # print(self.column.get_column_name())
            self.column_name = self.column.get_column_name()
            # print(self.column_name)

    def make_schema(self,
                    with_name_column=False,
                    with_object=True):
        self.to_string()
        schema_reference = {
            'ref_to_table': self.table_name,
            'ref_to_column_table': self.column_name,
            'on_delete': self.on_delete,
            'on_update': self.on_update
        }
        if with_object:
            schema_reference['object'] = self
        return schema_reference

    def make_sql_request(self,
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

    def __eq__(self, other):
        if not isinstance(other, Reference):
            # don't attempt to compare against unrelated types
            return False
        return self.on_delete == other.on_delete \
               and self.on_update == other.on_update \
               and self.table_name == other.table_name \
               and self.column_name == other.column_name

    def __str__(self):
        return '<Reference to {}.{}>'.format(self.table_name,
                                             self.column_name)
