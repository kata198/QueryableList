
def filterDictToStr(filterDict):
    return ', '.join(['%s=%s' %(key, repr(value)) for key, value in filterDict.items()])

class DataObject(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return 'DataObject( %s )' %(', '.join(['%s=%s' %(key, repr(value)) for key, value in self.__dict__.items()]))

    __repr__ = __str__
