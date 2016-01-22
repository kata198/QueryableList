
from QueryableList import QueryableListDicts, QueryableListObjs, QueryBuilder
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
        return 'SampleDataObj(**' + str(self.__dict__) + ')'

    __repr__ = __str__

if __name__ == '__main__':

    #data = [{'colour': 'purple', 'age': 31, 'name': 'Tim', 'likes' : ['puppies', 'rainbows']}, {'colour': None, 'age': 19, 'name': 'Joe', 'likes' : ['puppies', 'cars']}, {'colour': 'PURPLE', 'age': 23, 'name': 'Joe', 'likes' : ['cheese', 'books']}]

    # A straight dataset, can be optimized for object-only access
    data = [
        SampleDataObj(colour='purple', age=31, name='Tim', likes=['puppies', 'rainbows']),
        SampleDataObj(colour=None, age=19, name='Joe', likes=['puppies', 'cars']),
        SampleDataObj(colour='PURPLE', age=23, name='Joe', likes=['cheese', 'books']),
    ]

    # a mixed dataset of objects and dicts
    dataset2 = [ 
        SampleDataObj(colour='blue', age=25, name='Tim', likes=['batteries', 'cheese']),
        SampleDataObj(colour='red', age=55, name='Jack', likes=['puppies', 'milk']),
        {
            'colour' : 'green', 'age' : 88, 'name' : 'John', 'likes' : ['puppies', 'games']
        },
        {
            'colour' : 'orange', 'age' : 18, 'name' : 'Phil', 'likes' : ['puppies', 'gnomes']
        },
    ]

    
#    data = QueryableListDicts(data)
    data = QueryableListObjs(data)

    sys.stdout.write("Data: %s\n\n" %(data,))

    sys.stdout.write('People who are over 22 years old:\n%s\n\n' %(data.filter(age__gt=22),))

#    sys.stdout.write('People who like puppies or bricks, and their favourite colour is purple:\n\n' %(data.filter(likes__containsAny=('puppies', 'bricks')).filter(colour__ieq='purple'),))
    sys.stdout.write('People who like puppies or bricks, and their favourite colour is purple:\n%s\n\n' %(data.filter(likes__containsAny=('puppies', 'bricks'), colour__ieq='purple'),))

    sys.stdout.write('People who are at least 30 years old or like cheese:\n%s\n\n' %(data.filterOr(likes__contains='cheese', age__gte=30),))


    # Create a QueryBuilder to execute a query
    builder = QueryBuilder()
    builder.addFilter("AND", age__gt=22)
    builder.addFilter(likes__contains='puppies')

    # Execute on a QueryableList
    sys.stdout.write('Over 22 and likes puppies (dataset1):\n%s\n\n' %(str(builder.execute(data))))
    # Execute on a normal list, creating a QueryableListMixed
    sys.stdout.write('Over 22 and likes puppies (mixed dataset2):\n%s\n\n' %(str(builder.execute(dataset2))))


    #import pdb; pdb.set_trace()
