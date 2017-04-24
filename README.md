# QueryableList

What
====

QueryableList allows you to "filter" a list of items of varying types, simplifing code by replacing tedious for-loops with simple chaining.

It uses an interface common to some ORMs like Django, Flask, and IndexedRedis.

You can perform single filters on lists of data, or you can build queries and execute that query on any number of arbitrary data sets.

QueryableList also implements the boolean logic operators for lists (AND, OR, XOR) which can simplify your code.


**What pattern does it replace?**

Constant loops/getters to drill down data. If you are filtering data, displaying data by criteria, etc, your code will be FULL of these.

QueryableList simplifies and makes generic this common pattern of filtering.

*Before*

	def getOlderThan(people, minAge):

		ret = []
		for person in people: 
			if person.age and person.age > minAge:
				ret.append(person)
		return ret

	...
	people = getAllPeople() # Get your data  here
	oldEnoughToRide = getOlderThan(people, 13)
	notOldEnough =  [person for person in people if person not in oldEnoughToRide]


*After*

	people =  QueryableListObjs(  getAllPeople() )  # Transform data into QueryableList
	oldEnoughToRide =  people.filter(age__gt=13)
	notOldEnough =  people ^ oldEnoughToRide #  The XOR of the filtered list to the parent is the NOT of the filter criteria


No function, no loop, and list comprehensions can get very messy or impossible with a large number of complicated filters applied.

The above example shows a one-time filtering of a list. You can also build reusable queries, and append different criteria based on conditions or through passing the query around different functions. See "Building Reusable Queries" section below for more info.


How?
====


Types
-----

Perform one-time filters through one of the list-type extending classes:


**QueryableListObjs** - This assumes each item extends object [or implements \_\_getattribute\_\_].

**QueryableListDicts** - This assumes that each item is a dict [or implements \_\_getitem\_\_].

**QueryableListMixed** - QueryableList which can contain dict-like items or object-like item. (This is somewhat slower than using QueryableListObjs or QueryableListDicts directly, but use it if you need to mix, or need to support either type.)


The items within these lists do not need to be of the same type. If any fields are missing on the filtered objects, it will be assigned a value of "None" for filtering purposes.


Filter Methods
--------------

You can filter the data within these objects through one of the following methods:

*filterAnd* - returns a QueryableList where each item matches ALL of the provided criteria.

*filter* - Alias for filterAnd

*filterOr* - returns a QueryableList where each item matches ANY of the provided criteria.

*customFilter* - Takes a lambda or a function as a parameter. Each element in the list is passed into this function, and if it returns True, that element is retained.


The QueryableList types support all the operations of a list, and return the same QueryableList types so you can perform chaining. 

Additionally, you can use ADD(+), SUB(-), AND(&), OR(|), and XOR(^) operators against other QueryableLists as another powerful means of filtering.


You specify the filter operations by passing arguments of $fieldName\_\_$operation.

Example: e.x. results = objs.filter(name\_\_ne='Tim')  # get all objects where the 'name' field does not equal 'Tim'


For all available operations, see the "Operations" section below.


Other Methods
-------------

QueryableList collections have several other methods to make them as closely api-compatible with server-side filtering ORMs as possible.

This allows you to use the same functions regardless of if you are server-side or client-side filtering.

* count - Returns the number of items in this collection ( same as len(..) )

* all - Returns a copy of this collection, same elements but a new collection


Building Reusable Queries
-------------------------

You can build a reusable query, out of several chains of filters (either AND or OR) by using the **QueryBuilder** class.

The QueryBuilder class stores a "chain" of filters, which are applied in order. Each link in the chain contains a filter type (AND or OR), and the filters themselves (same as the filter methods on the QueryableList).


Use the *addFilter(filterType, ..filters..)* method to add a link to the chain. 

To execute the query, call *execute(lst)* , where "lst" is your list of items. You can execute a query multiple times on any number of datasets.

Use the *copy* method to create a copy of the current set of filters.


If you know the type in advance, you can pass a QueryableListObjs or QueryableListDicts when calling *execute* to slightly speed up access times, otherwise a *QueryableListMixed* (supports both dict and object style access) will be used.

Example:

	myQuery = QueryBuilder()
	myQuery.addFilter(age__gt=21)  # Age must be greater than 21
	myQuery.addFilter('OR', job__ieq='Manager', numSubordinates__gt=0) # Is a manager, or has more than 0 subordinates

	managerPartyCompany1 = myQuery.execute(company1Persons) # Filter from all company1Persons those that meet above criteria
	managerPartyCompany2 = myQuery.execute(company2Persons) # use same filter to apply same query to company2Persons


Extending QueryableList for your own data sets
----------------------------------------------

One of the powerful aspects of QueryableList is that it is easily extendable.

Generally, you won't need to do this, as QueryableListDicts or QueryableListObjs will handle your needs.

But sometimes, you have more advanced requirements than can be satisfied by properties and matching on them.

For these cases, you can extend QueryableList.QueryableListBase to create your own QueryableList type.

You only need to implement a single method, 


	@staticmethod
	def _get_item_value(item, fieldName)


"item" will be an item in your collection, and "fieldName" is the field being queried. 

For example, say you have a series of objects, "Job", which contain some attributes and a "queue".

You want to be able to filter on both the attributes on the object and various special attributes of it's queue (like size, item ids, etc).

You can implement like this:

	class MyJobCollection(QueryableList.QueryableListBase):

		@staticmethod
		def _get_item_value(item, fieldName):

			if fieldName == 'queueSize':
				# queueSize is the number of items in the queue
				return len(item.queue)
			elif fieldName == 'queueItemIds':
				# queueItemIds is a list of the ids in the item queue,
				#  so a "contains" query can check if an id is in this item's queue
				return [qi.id for qi in item.queue]
			elif hasattr(item, fieldName):
				# Otherwise, if this is an attribute on the item, return it's value
				if fieldName == 'queue':
					raise KeyError('Cannot query queue directly. Try queueSize or queueItemIds.')
				return getattr(item, fieldName)
			else:
				raise KeyError('Invalid attribute "%s" on %s' %(fieldName, item.__class__.__name__))

The init method takes a list of items (and it contains all the methods a list has, like *.append*), so you can create it like:

	myJob1 = MyQueue(...)
	myJob2 = MyQueue(...)

	myJobs = MyQueueCollection([myJob1, myJob2])

and use it like:

	largeJobs = myJobs.filter(queueSize__gt=10)

So just by implementing that one method, you now have all the powerful filter capabilities that QueryableList provides!



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

* icontains - Case-insensitive "contains"

* notcontains - Test that the item's field value does not contain the provided value ( using "not in" )

* noticontains - Case-insensitive "notcontains"

* containsAny - Test that the item's field value contains any of the items in the provided list ( using "in" )

* notcontainsAny - Test that the item's field value does not contain any of the items in the provided list ( using "not in" )

* splitcontains - Takes a tuple, (splitBy<str>, containsThis<str>). Use for a string that represents a list. The field will be split by the first, "splitBy", param, and the result tested that it contains an item matching the second, "containsThis", param. E.x. item\_\_splitcontains=(' ', 'someValue')

* splitnotcontains - Takes a tuple, (splitBy<str>, containsThis<str>). Use for a string that represents a list. The field will be split by the first, "splitBy", param, and the result tested that it does not contain an item matching the second, "containsThis", param.

* splitcontainsAny - Takes a tuple, (splitBy<str>, possibleMatches <list<str>>). Use for a string that represents a list. The field will be split by the first, "splitBy", param, and the result tested that it contains any of the items in the provided list.

* splitnotcontainsAny - Takes a tuple, (splitBy<str>, possibleMatches <list<str>>). Use for a string that represents a list. The field will be split by the first, "splitBy", param, and the result tested that it does not contains any of the items in the provided list.

* customMatch - Takes a lambda or function, which is passed in the value of the given field. If it returns True, the element is a match, otherwise it is not.


Full PyDoc Documentation
------------------------

Pydoc documentation can be found at: http://htmlpreview.github.io/?https://github.com/kata198/QueryableList/blob/master/doc/QueryableList.html?vers=4


