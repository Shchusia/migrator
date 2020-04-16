class Schema(object):
    def __init__(self):
        self.subclasses = dict()

    def get_sub_classes(self):
        self.subclasses = {cls.__name__: cls for cls in Schema.__subclasses__()}
