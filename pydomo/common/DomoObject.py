class DomoObject(dict):
    '''Superclass for DomoAPI objects. These are dict-like objects with
    predefined allowed fields.
    '''
    def __getattribute__(self, name):
        if name in super().__getattribute__('accepted_attrs'):
            return self.__getitem__(name)
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        self.__setitem__(name, value)

    def __setitem__(self, name, value):
        if name not in self.accepted_attrs:
            raise AttributeError("'{}' object has no attribute '{}'".format(
                                                    type(self).__name__, name))
        super().__setitem__(name, value)
