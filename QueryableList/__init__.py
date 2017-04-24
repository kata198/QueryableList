# Copyright (c) 2016, 2017 Timothy Savannah under the terms of the GNU Lesser General Public License version 2.1.
#  You should have received a copy of this as "LICENSE" with this source distribution.
#
# The full license is available at https://raw.githubusercontent.com/kata198/QueryableList/master/LICENSE

#vim: set ts=4 st=4 sw=4 expandtab
'''
    QueryableList - Allows adding ORM-style filter capabilities to ANY collection of data.

      Default implementations exist for list-of-objects (getattr-style) and list-of-dicts (getitem aka ['key'] style).

      The constructor takes a list of items, and a QueryableList supports all the list methods (like append, + operator, pop, etc)
        as well as additional methods (like subtract).

      To support your own complex types, simply extend "QueryableListBase" and implement a single method:

      _get_item_value(item, fieldName)

      where item is the object, fieldName is the name of field being queried ( e.x.  myCol.filter(size__gt=5)  fieldName would be just "size" )

      and the function fetches and returns the value off object. That's it!
      
      Now you support ALL the operations available in QueryableList, acting on your objects!
'''

__all__ = ('FILTER_TYPES', 'FILTER_METHOD_OR', 'FILTER_METHOD_OR', 'FILTER_METHODS', 'QueryableListObjs', 'QueryableListDicts', 'QueryableListBase', 'QueryableListMixed', 'QueryBuilder')

__version__ = '3.1.0'
__version_tuple__ = (3, 1, 0)


from .constants import FILTER_TYPES, FILTER_METHODS, FILTER_METHOD_OR, FILTER_METHOD_OR

from .Base import QueryableListBase
from .Builder import QueryBuilder


class QueryableListObjs(QueryableListBase):
    '''
        QueryableListObjs - QueryableList where each item extends object (or implements __getattribute__)
    '''

    @staticmethod
    def _get_item_value(item, fieldName):
        '''
            _get_item_value - Returns the value of a given field on #item, using object attribute-style access (getattr)

                @param item <???> - The item that needs a value fetched off it. items must support __getattribute__
                @param fieldName <str> - The name of the field on that item which is being requested

            @return - The value of the #fieldName attribute on #item

        '''
        return getattr(item, fieldName, None)


class QueryableListDicts(QueryableListBase):
    '''
        QueryableListDicts - QueryableList where each item is or extends dict (or implements __getitem__ and __contains__)
    '''


    @staticmethod
    def _get_item_value(item, fieldName):
        '''
            _get_item_value - Returns the value of a given field on #item, using dict-style access (e.x. x['a']) aka implements __getitem__

                @param item <???> - The item that needs a value fetched off it. items must support __getitem__
                @param fieldName <str> - The name of the field on that item which is being requested

            @return - The value of the #fieldName key on #item

        '''
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
        '''
            _get_item_value - Returns the value of a given field on #item, using either dict style (e.x. x['a']) aka __getitem__ access if possible,
              otherwise attribute access (aka implements __getattribute__).

              This allows you to pass a mix of object types, or objects and dicts, in the same collection.

                @param item <???> - The item that needs a value fetched off it. items must support either __getitem__ or __getattribute__
                @param fieldName <str> - The name of the field on that item which is being requested

            NOTE: if __getitem__ is defined, it will be used, otherwise __getattribute__ will be used.

            @return - The value of the #fieldName key/attribute on #item
        '''

        if hasattr(item, '__getitem__'):
            return QueryableListDicts._get_item_value(item, fieldName)

        return QueryableListObjs._get_item_value(item, fieldName)

#vim: set ts=4 st=4 sw=4 expandtab
