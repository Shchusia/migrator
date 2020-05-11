from migrant._utils.helper import check_2_dicts
from datetime import datetime
import time

class MigType(object):

    @classmethod
    def get_type(cls):
        return cls.__name__

    def get_extra_options(self):
        return dict()

    def get_db_equivalent(self, db_type):
        if hasattr(db_type.conformity, (self.get_type() + '_TYPE').upper()):
            try:
                return self.db_equivalent(db_type)
            except NotImplementedError:
                return getattr(db_type.conformity, (self.get_type() + '_TYPE').upper())
        else:
            raise NotImplementedError

    def db_equivalent(self, db_type):
        raise NotImplementedError

    def to_string(self, db_type):
        return self.get_db_equivalent(db_type)

    def _get_attributes(self):
        data_attributes = dict()
        for attribute in dir(self):
            if attribute[1] == '_':
                continue
            elif callable(getattr(self, attribute)):
                continue
            data_attributes[attribute] = getattr(self, attribute)
        return data_attributes

    def __eq__(self, other):
        if isinstance(other, type):
            other = other()
        if not isinstance(other, MigType):
            return False
        elif self.get_type() != other.get_type():
            return False
        else:
            self_attributes = self._get_attributes()
            other_attributes = other._get_attributes()
            result_compare_dicts = check_2_dicts(self_attributes,
                                                 other_attributes)
            if result_compare_dicts:
                return False
            return True

    def convert_value(self, value):
        return value

    def is_correct_value(self, value):
        return True


class OtherType(MigType):

    def __init__(self, full_string_type_on_db):
        self.str_type = full_string_type_on_db

    def db_equivalent(self, db_type):
        return self.str_type


class Text(MigType):

    def db_equivalent(self, db_type):
        return db_type.conformity.TEXT_TYPE

    def convert_value(self, value):
        return str(value)

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            return True
        except:
            return False


class Varchar(MigType):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            self.len_string = args[0]
        else:
            self.len_string = kwargs.get('len_string', None)

    def db_equivalent(self, db_type):
        return db_type.conformity.VARCHAR_TYPE + \
               '({})'.format(self.len_string) if self.len_string else ''

    def get_extra_options(self):
        return {
            'len_string': self.len_string
        }

    def convert_value(self, value):
        return str(value)

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            if self.len_string is None:
                return True
            else:
                return len(val) < self.len_string
        except:
            return False


class Char(MigType):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            self.len_string = args[0]
        else:
            self.len_string = kwargs.get('len_string')

    def db_equivalent(self, db_type):
        return db_type.conformity.CHAR_TYPE + \
               '({})'.format(self.len_string) if self.len_string else ''

    def get_extra_options(self):
        return {
            'len_string': self.len_string
        }

    def convert_value(self, value):
        return str(value)

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            if self.len_string is None:
                return True
            else:
                return len(val) < self.len_string
        except:
            return False


class Int(MigType):
    def __init__(self, *args, **kwargs):
        pass

    def db_equivalent(self, db_type):
        raise NotImplementedError

    def convert_value(self, value):
        return int(value)

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            return True
        except:
            return False


class Timestamp(MigType):
    def __init__(self, *args, **kwargs):
        self.with_time_zone = kwargs.get('with_time_zone', None)

    def get_extra_options(self):
        return {
            'with_time_zone': self.with_time_zone
        }

    def db_equivalent(self, db_type):
        if self.with_time_zone is None:
            additional_str = ''
        elif self.with_time_zone:
            additional_str = ' with time zone '
        else:
            additional_str = ' without time zone '
        return db_type.conformity.TIMESTAMP_TYPE + additional_str

    def convert_value(self, value):
        return value

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            return True
        except:
            return False


class Date(MigType):
    def db_equivalent(self, db_type):
        raise db_type.conformity.DATE_TYPE

    def convert_value(self, value):
        return value.date().isoformat()

    def is_correct_value(self, value):
        return isinstance(value, datetime.date)


class Time(MigType):
    def __init__(self, *args, **kwargs):
        self.with_time_zone = kwargs.get('with_time_zone', None)

    def get_extra_options(self):
        return {
            'with_time_zone': self.with_time_zone
        }

    def db_equivalent(self, db_type):
        if self.with_time_zone is None:
            additional_str = ''
        elif self.with_time_zone:
            additional_str = ' with time zone '
        else:
            additional_str = ' without time zone '
        return db_type.conformity.TIMESTAMP_TYPE + additional_str

    def is_correct_value(self, value):
        return isinstance(value, time)

class Decimal(MigType):
    def db_equivalent(self, db_type):
        return db_type.conformity.DECIMAL_TYPE

    def convert_value(self, value):
        return float(value)

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            return True
        except:
            return False


class Float(MigType):
    def db_equivalent(self, db_type):
        return db_type.conformity.FLOAT_TYPE

    def convert_value(self, value):
        return float(value)

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            return True
        except:
            return False


class TinyInt(MigType):
    def db_equivalent(self, db_type):
        return db_type.conformity.TINYINT_TYPE

    def convert_value(self, value):
        return int(value)

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            return True
        except:
            return False


class Numeric(MigType):
    def db_equivalent(self, db_type):
        return db_type.conformity.NUMERIC_TYPE

    def convert_value(self, value):
        return int(value)

    def is_correct_value(self, value):
        try:
            val = self.convert_value(value)
            return True
        except:
            return False
