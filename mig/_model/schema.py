from pprint import pprint
from .model import Column, Reference
from _utils.helper import get_class_name


class Schema(object):
    def __init__(self, db_instance,
                 is_print_sub_classes=False):
        self.subclasses = dict()
        self.get_sub_classes()
        if is_print_sub_classes:
            self.print_sub_classes()
        self.db_instance = db_instance
        self.current_state_schema = SchemaCurrentState(self.db_instance)

    def get_sub_classes(self):
        self.subclasses = {cls.__name__: cls for cls in Schema.__subclasses__()}

    def print_sub_classes(self):
        pprint(self.subclasses)

    def make_current_state_schema(self):
        self.current_state_schema.make_schema_by_classes(self.subclasses)

    def get_current_schema(self, with_objects=True):
        self.current_state_schema.make_schema_by_classes(self.subclasses,
                                                         with_objects)
        return self.current_state_schema.current_schema



class SchemaFileState(object):
    def __init__(self, db_instance):
        self.db_instance = db_instance

    pass

    def make_schema_by_files(self):
        pass


class SchemaCurrentState(object):
    def __init__(self, db_instance, ):
        self.db_instance = db_instance
        self.current_schema = dict()

    def make_schema_by_classes(self,
                               subclasses,
                               with_objects=True):
        """
        dict class_name: cls
        :param subclasses:
        :param with_objects
        :return:
        """
        migration_schema = dict()
        for clazz in subclasses.keys():
            current_class = subclasses[clazz]
            name_table = get_class_name(current_class)
            # print(name_table)
            # print('#######')
            schema_table = dict()
            for attribute, value in current_class.__dict__.items():
                if isinstance(value, Column):
                    value.set_column_name(attribute)
                    res = value.make_schema(with_object=with_objects)
                    schema_table[attribute] = res
            migration_schema[name_table] = schema_table
        # pprint(migration_schema)
        Reference.check_correct_references_in_schema(migration_schema)
        self.current_schema = migration_schema




