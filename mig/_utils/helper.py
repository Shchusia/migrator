import dictdiffer
import json


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


def save_to_json(data_to_save, path_to_save):
    with open(path_to_save, 'w') as fp:
        json.dump(data_to_save, fp)


def download_json(path_to_file):
    data = dict()
    with open(path_to_file, 'r', ) as file:
        data = json.load(file)
    return data


if __name__ == '__main__':
    pass
