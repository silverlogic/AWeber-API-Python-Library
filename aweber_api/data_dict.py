class DataDict(object):

    def __init__(self, data, name, parent):
        self.parent = parent
        self.data = data
        self.name = name

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.parent.__setattr__(self.name, self.data)
