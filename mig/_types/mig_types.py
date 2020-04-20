class MiType(type):
    def __new__(mcls, name, bases, attrs):

        if name.startswith('None'):
            return None

        # Go over attributes and see if they should be renamed.
        newattrs = {}
        for attrname, attrvalue in attrs.iteritems():
            if getattr(attrvalue, 'is_hook', 0):
                newattrs['__%s__' % attrname] = attrvalue
            else:
                newattrs[attrname] = attrvalue

        return super(MiType, mcls).__new__(mcls, name, bases, newattrs)

    def __init__(self, name, bases, attrs):
        super(MiType, self).__init__(name, bases, attrs)

        # classregistry.register(self, self.interfaces)

    def __add__(self, other):
        class AutoClass(self, other):
            pass
        return AutoClass


class MiigType(MiType):
    __metaclass__ = MiType


class MigType(object):

    @classmethod
    def get_type(cls):
        return cls.__name__

    def get_extra_options(self):
        return dict()

    def get_db_equivalent(self, db_type):
        if hasattr(db_type.conformity, (self.get_type()+'_TYPE').upper()):
            try:
                return self.db_equivalent(db_type)
            except NotImplementedError:
                return getattr(db_type.conformity, (self.get_type()+'_TYPE').upper())
        else:
            raise NotImplementedError

    def db_equivalent(self, db_type):
        raise NotImplementedError

    def to_string(self, db_type):
        return self.get_db_equivalent(db_type)


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
        return db_type.conformity.VARCHAR_TYPE +\
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
        return db_type.conformity.CHAR_TYPE +\
               '({})'.format(self.len_string) if self.len_string else ''

    def get_extra_options(self):
        return {
            'len_string': self.len_string
        }


class Int(MigType):
    def __init__(self, *args, **kwargs):
        pass
    pass


if __name__ == '__main__':
    c = Char(7)
    print(c.get_type())
    print(c.get_extra_options())
    c2 = Char(**c.get_extra_options())
    print(c2.get_extra_options())