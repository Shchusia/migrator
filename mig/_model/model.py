class Model(object):
    def __init__(self):
        pass

    def get_sub_classes(self):
        print([cls.__name__ for cls in Model.__subclasses__()])