# Copyright (c) 2016, 2017 Timothy Savannah under the terms of the GNU Lesser General Public License version 2.1.
#  You should have received a copy of this as "LICENSE" with this source distribution.
#  The full license is available at https://raw.githubusercontent.com/kata198/QueryableList/master/LICENSE
#
# TODO: Add tests for QueryBuilder
'''
    Builder - Provides "QueryBuilder", which supports building reuaable queries which can be reused and executed
      on datasets.

'''

#vim: set ts=4 st=4 sw=4 expandtab

import copy
from collections import namedtuple, deque

from .Base import getFiltersFromArgs, QueryableListBase

from .constants import FILTER_METHODS, FILTER_METHOD_AND, FILTER_METHOD_OR

class QueryBuilder(object):
    '''
        QueryBuilder - Build a reusable query that can be applied on multiple lists, or appended
            by several methods.

            If you are going to perform the same filter a bunch of times, use QueryBuilder to save
              the cost of constructing the query each time.
        '''

    def __init__(self):
        self.filters = deque()

    def addFilter(self, filterMethod=FILTER_METHOD_AND, **kwargs):
        '''
            addFilter - Add a filter to this query.

            @param filterMethod  <str> - The filter method to use (AND or OR), default: 'AND'
            @param additional args - Filter arguments. @see QueryableListBase.filter

            @raises ValueError if filterMethod is not one of known methods.

        '''
        filterMethod = filterMethod.upper()
        if filterMethod not in FILTER_METHODS:
            raise ValueError('Unknown filter method, %s. Must be one of: %s' %(str(filterMethod), repr(FILTER_METHODS)))

        self.filters.append((filterMethod, kwargs))

    def addFilterAnd(self, **kwargs):
        '''
            addFilterAnd - Adds an AND filter. Alias for #addFilter(filterMethod=FILTER_METHOD_AND, ...)

            @see #addFilter
        '''
        return self.addFilter(FILTER_METHOD_AND, **kwargs)

    def addFilterOr(self, **kwargs):
        '''
            addFilterOr - Adds an OR filter, Alias for #addFIlter(filterMethod=FILTER_METHOD_OR, .,.)

            @see #andFilter
        '''
        return self.addFilter(FILTER_METHOD_OR, **kwargs)

    def execute(self, lst):
        '''
            execute - Execute the series of filters, in order, on the provided list.

            @param lst <list/ A QueryableList type> - The list to filter. If you already know the types of items within
                the list, you can pick a QueryableList implementing class to get faster results. Otherwise, if a list type that does
                not extend QueryableListBase is provided, QueryableListMixed will be used (Supports both object-like and dict-like items)

            @return - QueryableList of results. If you provided #lst as a QueryableList type already, that same type will be returned.
                Otherwise, a QueryableListMixed will be returned.
        '''
        from . import QueryableListMixed
        if not issubclass(lst.__class__, QueryableListBase):
            lst = QueryableListMixed(lst)
        filters = copy.copy(self.filters)
        nextFilter = filters.popleft()
        while nextFilter:
            (filterMethod, filterArgs) = nextFilter
            lst = self._applyFilter(lst, filterMethod, filterArgs)
            if len(lst) == 0:
                return lst
            try:
                nextFilter = filters.popleft()
            except:
                break
        return lst

    def copy(self):
        '''
            copy - Create a copy of this query.
        
            @return <QueryBuilder> - a copy of this query
        '''
        ret = QueryBuilder()
        ret.filters = copy.copy(self.filters)
        return ret

    @staticmethod
    def _applyFilter(lst, filterMethod, filterArgs):
        '''
            _applyFilter - Applies the given filter method on a set of args

             private method - used by execute

             @return QueryableList - a QueryableList containing the elements of the resulting filter
        '''
        if filterMethod == FILTER_METHOD_AND:
            return lst.filterAnd(**filterArgs)
        else: # ALready validated in addFIlter that type is AND or OR
            return lst.filterOr(**filterArgs)


#vim: set ts=4 st=4 sw=4 expandtab
