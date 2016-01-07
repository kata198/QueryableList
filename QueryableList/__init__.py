# Copyright (c) 2016 Timothy Savannah under the terms of the GNU Lesser General Public License version 2.1.
#  You should have received a copy of this as "LICENSE" with this source distribution.
'''

    QueryableList - Add support for ORM-style filtering to any list of items.


    Use through one of the list-type extending classes:


        QueryableListObjs - This assumes each item is an object [or implements __getattribute__].

        QueryableListDicts - This assumes that each item is a dict [or implements __getitem__].


    You can filter these objects by using the method "filterAnd" (or its alias, "filter"), or "filterOr".

    filterAnd returns a QueryableList where each item matches ALL of the provided criteria.
    filterOr returns a QueryableList where each item matches ANY of the provided criteria.

    You specify the filter operations by passing arguments of $fieldName__$operation (e.x. results = objs.filter(name__ne='Tim') ), where "$fieldName" matches the name of an attribute/key and "$operation" is one of the following:


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

'''

__all__ = ('FILTER_TYPES', 'QueryableListObjs', 'QueryableListDicts', 'QueryableListBase')

# FILTER_TYPES - All available filter types
FILTER_TYPES = {'eq', 'ieq', 'ne', 'ine', 'lt', 'gt', 'lte', 'gte', 'isnull', 'is', 'isnot', 'in', 'notin', 'contains', 'notcontains', 'containsAny', 'notcontainsAny'}

from .Base import QueryableListBase


class QueryableListObjs(QueryableListBase):
    '''
        QueryableListObjs - QueryableList where each item extends object (or implements __getattribute__)
    '''

    _get_item_value = getattr

#    @staticmethod
#    def _get_item_value(item, fieldName):
#        return getattr(item, fieldName)


class QueryableListDicts(QueryableListBase):
    '''
        QueryableListDicts - QueryableList where each item is or extends dict (or implements __getitem__)
    '''


    @staticmethod
    def _get_item_value(item, fieldName):
        return item[fieldName]
