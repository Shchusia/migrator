class RowColumn():
    def set_value(self):
        pass

class RowTable:
    def __init__(self, name_table):
        self.name_table = name_table
        self.columns = list()

    def append_column(self, column):
        self.columns.append(column)
