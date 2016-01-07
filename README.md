# QueryableList
Python module to add support for ORM-style filtering to any list of items. You can use and chain multiple types of filter expressions without several loops in order to greatly simplify the filtering of objects.


Use through one of the list-type extending classes:


**QueryableListObjs** - This assumes each item extends object [or implements \_\_getattribute\_\_].

**QueryableListDicts** - This assumes that each item is a dict [or implements \_\_getitem\_\_].


You can filter these objects by using the method "filterAnd" (or its alias, "filter"), or "filterOr".

*filterAnd* - returns a QueryableList where each item matches ALL of the provided criteria.

*filterOr* - returns a QueryableList where each item matches ANY of the provided criteria.


The QueryableList types support all the operations of a list, and return the same QueryableList types so you can perform chaining. QueryableList also supports subtraction, whereas normal lists do not.

Items filtered do not need to be of the same type.
If you filter on a field and it is not present on a member, the value of that field is assumed None (null) for comparison purposes.


You specify the filter operations by passing arguments of $fieldName\_\_$operation (e.x. results = objs.filter(name\_\_ne='Tim') ), where "$fieldName" matches the name of an attribute/key and "$operation" is one of the following:


Operations
----------

* eq - Test equality ( = operator )

* ieq - Test equality, ignoring case (must be strings, or at least implement the .lower() method)

* ne  - Test inequality ( != operator )

* ine - Test inequality, ignoring case (must be strings, or at least implement the .lower() method)

* lt  - The item's field value must be less than the provided value

* lte - The item's field value must be less than or equal to the provided value

* gt  - The item's field value must be greater than the provided value

* gte - The item's field value must be greater than or equal to the provided value

* isnull - Provided value must be True/False. If True, the item's field value must be None, otherwise it must not be None.

* is  - Test identity equality ( is operator )

* isnot - Test identity inequality ( is not operator )

* in - Test that the item's field value is contained in the provided list of items

* notin - Test that the item's field value is not contained in the provided list of items

* contains - Test that the item's field value contains the provided value ( using "in" )

* notcontains - Test that the item's field value does not contain the provided value ( using "not in" )

* containsAny - Test that the item's field value contains any of the items in the provided list ( using "in" )

* notcontainsAny - Test that the item's field value does not contain any of the items in the provided list ( using "not in" )


Full Documentation
------------------

Pydoc documentation can be found at: http://htmlpreview.github.io/?https://github.com/kata198/QueryableList/blob/master/doc/QueryableList.html?vers=1


Example
-------

Here is an example with some simple, silly data, doing some filters, followed by the results.

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


		#data = QueryableListDicts(data)
		data = QueryableListObjs(data)

		sys.stdout.write("Data: %s\n\n" %(data,))

		sys.stdout.write('People who are over 22 years old:\n%s\n\n' %(data.filter(age__gt=22),))

		#sys.stdout.write('People who like puppies or bricks, and their favourite colour is purple:\n\n' %(data.filter(likes__containsAny=('puppies', 'bricks')).filter(colour__ieq='purple'),))
		sys.stdout.write('People who like puppies or bricks, and their favourite colour is purple:\n%s\n\n' %(data.filter(likes__containsAny=('puppies', 'bricks'), colour__ieq='purple'),))

		sys.stdout.write('People who are at least 30 years old or like cheese:\n%s\n\n' %(data.filterOr(likes__contains='cheese', age__gte=30),))


		#import pdb; pdb.set_trace()

**Results:**

	Data: QueryableListObjs([{'colour': 'purple', 'likes': ['puppies', 'rainbows'], 'age': 31, 'name': 'Tim'}, {'colour': None, 'likes': ['puppies', 'cars'], 'age': 19, 'name': 'Joe'}, {'colour': 'PURPLE', 'likes': ['cheese', 'books'], 'age': 23, 'name': 'Joe'}])

	People who are over 22 years old:
	QueryableListObjs([{'colour': 'purple', 'likes': ['puppies', 'rainbows'], 'age': 31, 'name': 'Tim'}, {'colour': 'PURPLE', 'likes': ['cheese', 'books'], 'age': 23, 'name': 'Joe'}])

	People who like puppies or bricks, and their favourite colour is purple:
	QueryableListObjs([{'colour': 'purple', 'likes': ['puppies', 'rainbows'], 'age': 31, 'name': 'Tim'}])

	People who are at least 30 years old or like cheese:
	QueryableListObjs([{'colour': 'purple', 'likes': ['puppies', 'rainbows'], 'age': 31, 'name': 'Tim'}, {'colour': 'PURPLE', 'likes': ['cheese', 'books'], 'age': 23, 'name': 'Joe'}])

