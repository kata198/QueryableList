# Copyright (c) 2016 Timothy Savannah under the terms of the GNU Lesser General Public License version 2.1.
#  You should have received a copy of this as "LICENSE" with this source distribution.
'''

    QueryableList - Add support for ORM-style filtering to any list of items.


    Use through one of the list-type extending classes:


        QueryableListObjs - This assumes each item is an object [or implements __getattribute__].

        QueryableListDicts - This assumes that each item is a dict [or implements __getitem__ and __contains__].

        QueryableListMixed - QueryableList which can contain dict-like items or object-like items 

            This is somewhat slower than using QueryableListObjs or QueryableListDicts directly, but use it if you need to mix, or need to support either type.


    You can filter these objects by using the method "filterAnd" (or its alias, "filter"), or "filterOr".

    filterAnd returns a QueryableList where each item matches ALL of the provided criteria.
    filterOr returns a QueryableList where each item matches ANY of the provided criteria.

    You specify the filter operations by passing arguments of $fieldName__$operation

    Example: results = objs.filter(name__ne='Tim')

    where "$fieldName" matches the name of an attribute/key and "$operation" is one of the following:


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

        * splitcontains - Takes a tuple, (splitBy<str>, containsThis<str>). Use for a string that represents a list. The field will be split by the first, "splitBy", param, and the result tested that it contains an item matching the second, "containsThis", param. E.x. item__splitcontains=(' ', 'someValue')


        * splitnotcontains - Takes a tuple, (splitBy<str>, containsThis<str>). Use for a string that represents a list. The field will be split by the first, "splitBy", param, and the result tested that it does not contain an item matching the second, "containsThis", param.

        * splitcontainsAny - Takes a tuple, (splitBy<str>, possibleMatches <list<str>>). Use for a string that represents a list. The field will be split by the first, "splitBy", param, and the result tested that it contains any of the items in the provided list.

        * splitnotcontainsAny - Takes a tuple, (splitBy<str>, possibleMatches <list<str>>). Use for a string that represents a list. The field will be split by the first, "splitBy", param, and the result tested that it does not contains any of the items in the provided list.
        


    If a member of the list does not contain a field, the value is assigned "Null" for comparison purposes.

'''

__all__ = ('FILTER_TYPES', 'QueryableListObjs', 'QueryableListDicts', 'QueryableListBase')

__version__ = '1.2.0'
__version_tuple__ = (1, 2, 0)

# FILTER_TYPES - All available filter types
FILTER_TYPES = {'eq', 'ieq', 'ne', 'ine', 'lt', 'gt', 'lte', 'gte', 'isnull', 'is', 'isnot', 
    'in', 'notin', 'contains', 'notcontains', 'containsAny', 'notcontainsAny',
    'splitcontains', 'splitnotcontains', 'splitcontainsAny', 'splitnotcontainsAny'}

from .Base import QueryableListBase


class QueryableListObjs(QueryableListBase):
    '''
        QueryableListObjs - QueryableList where each item extends object (or implements __getattribute__)
    '''

#    _get_item_value = getattr

    @staticmethod
    def _get_item_value(item, fieldName):
        return getattr(item, fieldName, None)


class QueryableListDicts(QueryableListBase):
    '''
        QueryableListDicts - QueryableList where each item is or extends dict (or implements __getitem__ and __contains__)
    '''


    @staticmethod
    def _get_item_value(item, fieldName):
        if fieldName in item:
            return item[fieldName]
        return None


class QueryableListMixed(QueryableListBase):
    '''
        QueryableListMixed - QueryableList which can contain dict-like items or object-like items 
        
            This is somewhat slower than using QueryableListObjs or QueryableListDicts directly, but use it if you need to mix, or need to support either type.
    '''

    @staticmethod
    def _get_item_value(item, fieldName):
        if hasattr(item, '__getitem__'):
            return QueryableListDicts._get_item_value(item, fieldName)

        return QueryableListObjs._get_item_value(item, fieldName)
