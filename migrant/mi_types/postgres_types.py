from migrant.mi_types.mi_types import MigType


class Json(MigType):
    def get_db_equivalent(self, db_type):
        return db_type.conformity.JSON_TYPE

    def db_equivalent(self, db_type):
        return db_type.conformity.JSON_TYPE


class Array(MigType):
    def __init__(self, *args, **kwargs):
        if len(args) == 0 and kwargs.get('mig_type_arr', None) is None:
            raise ValueError('please indicate type')
        mig_type_array = args[0] if len(args) != 0 else kwargs['mig_type_arr']

        if isinstance(mig_type_array, MigType) or isinstance(mig_type_array, dict):
            if isinstance(mig_type_array, MigType):
                self.mig_type_arr = mig_type_array
            else:
                subclasses = {cls.__name__: cls for cls in MigType.__subclasses__()}
                self.mig_type_arr = subclasses[kwargs['mig_type_arr']['type_name']](
                    **kwargs['mig_type_arr']['type_extra_options'])
        else:
            raise TypeError('not correct type in array')

        if len(args) > 1:
            self.size = args[1]
        else:
            self.size = kwargs.get('size', '')
        if self.size != '':
            try:
                int(self.size)
            except:
                raise TypeError('not correct type for size array')

    def get_db_equivalent(self, db_type):
        return self.mig_type_arr.get_db_equivalent(db_type) + '[' + str(self.size) + ']'

    def db_equivalent(self, db_type):
        return self.get_db_equivalent(db_type)

    def get_extra_options(self):
        return {
            'mig_type_arr': {
                'type_name': self.mig_type_arr.get_type(),
                'type_extra_options': self.mig_type_arr.get_extra_options()
            },
            'size': self.size,
        }


class Serial(MigType):
    def get_db_equivalent(self, db_type):
        return 'SERIAL'

    def db_equivalent(self, db_type):
        return 'SERIAL'


class BigSerial(MigType):
    def get_db_equivalent(self, db_type):
        return 'BIGSERIAL'

    def db_equivalent(self, db_type):
        return 'BIGSERIAL'


class Boolean(MigType):
    def get_db_equivalent(self, db_type):
        return 'BOOLEAN'

    def db_equivalent(self, db_type):
        return 'BOOLEAN'


class Money(MigType):
    def get_db_equivalent(self, db_type):
        return 'MONEY'

    def db_equivalent(self, db_type):
        return 'MONEY'


class Numeric(MigType):
    def __init__(self, precision=None, scale=None, *args, **kwargs):
        self.precision = precision
        self.scale = scale
        if self.precision:
            try:
                self.precision = int(self.precision)
                if self.precision <= 0:
                    raise ValueError('The precision must be positive')
            except:
                raise TypeError('incorrect type precision for Numeric.')
        if self.scale:
            try:
                self.scale = int(self.scale)
                if self.scale < 0:
                    raise ValueError('The scale must be zero or positive')
            except:
                raise TypeError('incorrect type scale for Numeric.')
        if self.precision is None and self.scale is not None:
            self.precision = 0

    def db_equivalent(self, db_type):
        additional = ''
        if self.precision:
            additional += str(self.precision)
        if self.scale:
            additional += ',' + str(self.scale)
        if additional:
            additional = '(' + additional + ')'
        return 'NUMERIC' + additional

    def get_extra_options(self):
        return {
            'scale': self.scale,
            'precision': self.precision
        }
