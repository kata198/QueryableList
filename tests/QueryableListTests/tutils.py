'''
    tutils - Common test functions used by multiple tests
'''

# vim: set ts=4 st=4 sw=4 expandtab :
def filterDictToStr(filterDict):
    return ', '.join(['%s=%s' %(key, repr(value)) for key, value in filterDict.items()])

class DataObject(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return 'DataObject( %s )' %(', '.join(['%s=%s' %(key, repr(value)) for key, value in self.__dict__.items()]))

    __repr__ = __str__


class hashableDict(dict):
    '''
        A dict that is hashable.
    '''

    def __hash__(self):
        KEYVAL_SEP = '~~..~~'
        NONEVAL='~~__NONE$$zz'

        PAIRS_SEP='88ascvjikZZ'

        hashableStr = []

        keys = list(self.keys())
        keys.sort()

        for key in keys:
            value = self[key]

            if value is None:
                value = NONEVAL
            else:
                value = str(value)

            hashableStr.append(key + KEYVAL_SEP + value)

        hashableStr = PAIRS_SEP.join(hashableStr)

        ret = hash(hashableStr)
        return ret


def assembleItems(item, nums):
    return [item[num] for num in nums]
