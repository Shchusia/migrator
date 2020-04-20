import dictdiffer


def get_class_name(current_class):
    name_table = str(current_class.__name__).lower() \
        if not hasattr(current_class, '__tablename__') \
        else current_class.__tablename__
    return name_table


def check_2_dicts(dict1, dict2):
    diff_str = ''
    for diff in list(dictdiffer.diff(dict1, dict2)):
        diff_str += str(diff) + ' | '
    return diff_str


if __name__ == '__main__':
    a_dict = {'user': {'id': {'column_object': '<_model.model.Column object at 0x000001A611B73748>',
                 'type': 'Int',
                 'type_extra_options': {}},
          'name': {'column_object': '<_model.model.Column object at 0x000001A611C3AEB8>',
                   'type': 'Varchar',
                   'type_extra_options': {'len_string': 5}}},
 'user_additional_info': {'ref_user': {'column_object': '<_model.model.Column object at 0x000001A611CC0DA0>',
                                       'reference': {'on_delete': 'cascade',
                                                     'on_update': None,
                                                     'ref_to_column_table': 'id',
                                                     'ref_to_table': 'user'},
                                       'type': 'Int',
                                       'type_extra_options': {}}},
 'userinfo': {'address': {'column_object': '<_model.model.Column object at 0x000001A611CABBE0>',
                          'type': 'Text',
                          'type_extra_options': {}},
              'ref_user': {'column_object': '<_model.model.Column object at 0x000001A611CC04E0>',
                           'reference': {'on_delete': 'cascade',
                                         'on_update': 'SET NULL',
                                         'ref_to_column_table': 'id',
                                         'ref_to_table': 'user'},
                           'type': 'Int',
                           'type_extra_options': {}}}}


    b_dict = {'user': {'id': {'column_object': '<_model.model.Column object at 0x000001CC7F493518>',
                 'type': 'Int',
                 'type_extra_options': {}},
          'name': {'column_object': '<_model.model.Column object at 0x000001CC7F55AE80>',
                   'type': 'Varchar',
                   'type_extra_options': {'len_string': 5}}},
 'user_additional_info': {'ref_user': {'column_object': '<_model.model.Column object at 0x000001CC7F5E0CC0>',
                                       'reference': {'on_delete': 'cascade',
                                                     'on_update': None,
                                                     'ref_to_column_table': 'id',
                                                     'ref_to_table': 'user'},
                                       'type': 'Int',
                                       'type_extra_options': {}}},
 'userinfo': {'address': {'column_object': '<_model.model.Column object at 0x000001CC7F5CBB00>',
                          'type': 'Text',
                          'type_extra_options': {}},
              'ref_user': {'column_object': '<_model.model.Column object at 0x000001CC7F5E0470>',
                           'reference': {'on_delete': 'cascade',
                                         'on_update': 'SET NULL',
                                         'ref_to_column_table': 'id',
                                         'ref_to_table': 'user'},
                           'type': 'Int',
                           'type_extra_options': {}}}}
    print(check_2_dicts(b_dict, a_dict))