from migrant.mi_types.mi_types import MigType
from migrant.model.model import Model
from migrant.model.reference import Reference


# from sqlalchemy import Column as ColumnAlchemy
class Column(Model
             # , ColumnAlchemy
             ):
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
                 **kwargs):
        # super().__init__(**kwargs)
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
        self.value = None

    def __hash__(self):
        return hash((self.column_name, self.column.get_type(),))

    def __str__(self):
        return '<Column: {}:{}>'.format(self.column_name, self.column.get_type())

    def __eq__(self, other):
        if not isinstance(other, Column):
            return False
        is_eq_references = self.reference == other.reference
        is_eq_column = self.column == other.column
        is_eq_check = self.check == other.check
        is_eq_column_name = self.column_name == other.column_name
        is_eq_additional_str_parameter = self.additional_str_parameter == other.additional_str_parameter
        is_eq_is_not_null = self.is_not_null == other.is_not_null
        is_eq_default = self.default == other.default
        is_eq_unique = self.unique == other.unique
        is_eq_primary_key = self.primary_key == other.primary_key
        is_eq_value = self.value == other.value
        return is_eq_references \
               and is_eq_column \
               and is_eq_check \
               and is_eq_column_name \
               and is_eq_additional_str_parameter \
               and is_eq_is_not_null \
               and is_eq_default \
               and is_eq_unique \
               and is_eq_primary_key \
               and is_eq_value

    def set_column_name(self,
                        name_atr):
        self.column_name = name_atr

    def set_value(self, value):
        self.value = value

    def get_column_name(self):
        return self.column_name

    def get_column_type(self):
        return self.column.get_type()

    def get_value(self):
        return self.value

    def make_schema(self,
                    with_name_column=False,
                    with_object=True):
        column_dict = {
            'column_name': self.column_name,
            'column_type': self.column.get_type(),
            'type_extra_options': self.column.get_extra_options()
        }
        if with_object:
            column_dict['object'] = self
        if self.default:
            column_dict['default'] = self.default
        if self.is_not_null:
            column_dict['is_not_null'] = self.is_not_null
        if self.unique:
            column_dict['unique'] = self.unique
        if self.primary_key:
            column_dict['primary_key'] = self.primary_key
        if self.reference:
            column_dict['reference'] = self.reference.make_schema(with_object=with_object)
        if self.check:
            column_dict['check'] = self.check
        if self.additional_str_parameter:
            column_dict['additional_str_parameter'] = self.additional_str_parameter
        if with_name_column:
            return {
                self.column_name: column_dict
            }
        return column_dict

    def make_sql_request(self,
                         db_instance,
                         is_add_primary_key=True):
        """

        :param db_instance:
        :param is_add_primary_key: parameter for tables where many primary keys
        :return:
        """
        column = '{} {}'.format(self.column_name,
                                self.column.get_db_equivalent(db_instance))
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
            column += self.reference.make_sql_request(db_instance)
        return column

    def alter_table(self, name_table, alter_action, db_instance, **kwargs):
        str_up = db_instance.conformity.alter_table(name_table=name_table,
                                                    column=self,
                                                    alter_action=alter_action,
                                                    db=db_instance,
                                                    **kwargs)
        return str_up

    def is_correct_value(self):

        def correct_is_not_null():
            if self.is_not_null and self.value is None and self.default is None:
                return False
            return True

        def correct_value_type():
            return self.column.is_correct_value(self.value)

        return correct_is_not_null() \
               and correct_value_type()

    def value_to_insert(self):
        val = self.column.convert_value(self.value)
        if val is None:
            if self.primary_key:
                return 'DEFAULT'
            elif self.is_not_null:
                return 'DEFAULT'
            else:
                return 'NULL'
        return str(val)


class ColumnSchema(Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)