from migrant._utils.helper import check_2_dicts


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


class OtherType(MigType):

    def __init__(self, full_string_type_on_db):
        self.str_type = full_string_type_on_db

    def db_equivalent(self, db_type):
        return self.str_type


class Text(MigType):

    def db_equivalent(self, db_type):
        return db_type.conformity.TEXT_TYPE


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


class Int(MigType):
    def __init__(self, *args, **kwargs):
        pass

    pass
