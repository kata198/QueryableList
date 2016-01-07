
from QueryableList import QueryableListDicts, QueryableListObjs
import sys


class DataObj(object):
    pass

class SampleDataObj(object):

    def __init__(self, colour, age, name, likes):
        self.colour = colour
        self.age = age
        self.name = name
        self.likes = likes

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__

if __name__ == '__main__':

    #data = [{'colour': 'purple', 'age': 31, 'name': 'Tim', 'likes' : ['puppies', 'rainbows']}, {'colour': None, 'age': 19, 'name': 'Joe', 'likes' : ['puppies', 'cars']}, {'colour': 'PURPLE', 'age': 23, 'name': 'Joe', 'likes' : ['cheese', 'books']}]
    data = [
        SampleDataObj(colour='purple', age=31, name='Tim', likes=['puppies', 'rainbows']),
        SampleDataObj(colour=None, age=19, name='Joe', likes=['puppies', 'cars']),
        SampleDataObj(colour='PURPLE', age=23, name='Joe', likes=['cheese', 'books']),
    ]

    
#    data = QueryableListDicts(data)
    data = QueryableListObjs(data)

    sys.stdout.write("Data: %s\n\n" %(data,))

    sys.stdout.write('People who are over 22 years old:\n%s\n\n' %(data.filter(age__gt=22),))

#    sys.stdout.write('People who like puppies or bricks, and their favourite colour is purple:\n\n' %(data.filter(likes__containsAny=('puppies', 'bricks')).filter(colour__ieq='purple'),))
    sys.stdout.write('People who like puppies or bricks, and their favourite colour is purple:\n%s\n\n' %(data.filter(likes__containsAny=('puppies', 'bricks'), colour__ieq='purple'),))

    sys.stdout.write('People who are at least 30 years old or like cheese:\n%s\n\n' %(data.filterOr(likes__contains='cheese', age__gte=30),))


    #import pdb; pdb.set_trace()
