import hashlib
import time


class Migration(object):
    structure_file = {
        'previous_migration': None,
        'current_migration': '',
        'comment': '',
        'date': '',
        'who_make_migration': '',
    }

    def __init__(self):
        pass

    @staticmethod
    def get_name():
        str_name = '{}'.format(int(time.time()))
        hash_name = hashlib.md5(str_name.encode('utf-8')).hexdigest()[:10]
        return str_name + '_' + hash_name




if __name__ == '__main__':
    print(Migration.get_name())
