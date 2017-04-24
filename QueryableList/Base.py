# Copyright (c) 2016, 2017 Timothy Savannah under the terms of the GNU Lesser General Public License version 2.1.
#  You should have received a copy of this as "LICENSE" with this source distribution. The full license is available at https://raw.githubusercontent.com/kata198/QueryableList/master/LICENSE

#vim: set ts=4 st=4 sw=4 expandtab
from .constants import FILTER_TYPES

import re

__all__ = ('FILTER_PARAM_RE', 'getFiltersFromArgs', 'QueryableListBase')

FILTER_PARAM_RE = re.compile('^(?P<field>.+)__(?P<filterType>.+)$')

'''
    USE_CACHED - Set to True to cache field values on the items.

      I don't notice any performance difference with this on or off,
        so best to leave it False for now.
'''
USE_CACHED = False


def getFiltersFromArgs(kwargs):
    '''
        getFiltersFromArgs - Returns a dictionary of each filter type, and the corrosponding field/value

        @param kwargs <dict> - Dictionary of filter arguments


        @return - Dictionary of each filter type (minus the ones that are optimized into others), each containing a list of tuples, (fieldName, matchingValue)
    '''

    # Create a copy of each possible filter in FILTER_TYPES and link to empty list.
    #  This object will be filled with all of the filters requested
    ret = { filterType : list() for filterType in FILTER_TYPES }

    for key, value in kwargs.items():
        matchObj = FILTER_PARAM_RE.match(key)
        if not matchObj:

            # Default ( no __$oper) is eq
            filterType = 'eq'
            field = key

        else:

            # We have an operation defined, extract it, and optimize if possible
            #  (like if op is a case-insensitive, lowercase the value here)
            groupDict = matchObj.groupdict()

            filterType = groupDict['filterType']
            field = groupDict['field']


            if filterType not in FILTER_TYPES:
                raise ValueError('Unknown filter type: %s. Choices are: (%s)' %(filterType, ', '.join(FILTER_TYPES)))


            if filterType == 'isnull':
                # Convert "isnull" to one of the "is" or "isnot" filters against None
                if type(value) is not bool:
                    raise ValueError('Filter type "isnull" requires True/False.')

                if value is True:
                    filterType = "is"
                else:
                    filterType = "isnot"

                value = None
            elif filterType in ('in', 'notin'):
                # Try to make more efficient by making a set. Fallback to just using what they provide, could be an object implementing "in"
                try:
                    value = set(value)
                except:
                    pass
            # Optimization - if case-insensitive, lowercase the comparison value here
            elif filterType in ('ieq', 'ine', 'icontains', 'noticontains'):
                value = value.lower()
            elif filterType.startswith('split'):
                if (not issubclass(type(value), tuple) and not issubclass(type(value), list)) or len(value) != 2:
                    raise ValueError('Filter type %s expects a tuple of two params. (splitBy, matchPortion)' %(filterType,))



        ret[filterType].append( (field, value) )

    return ret



class QueryableListBase(list):
    '''
        QueryableListBase - The base implementation of a QueryableList. 

        Any implementing classes should only have to implement the "_get_item_value(item, fieldName)" method, to return the value of a given field on an item.

        You cannot use this directly, instead use one of the implementing classes (like QueryableListDicts or QueryableListObjs), or your own implementing class.
    '''

    def all(self):
        '''
            all - Returns all items in this collection, as the collection type (aka returns a copy of "self").

              This method is provided for method parity with ORMs that build a filter set with filter calls,
                and then execute with ".all" (like django or IndexedRedis).

              That way you can filter and call ".all()" after, and it doesn't matter if you're hitting the db
                or filtering already-fetched objects, the usage remains the same.

            @return <self.__class__> - self
        '''
        return self.__class__(self)


    @staticmethod
    def _get_item_value(item, fieldName):
        '''
            _get_item_value - Must be implemented to complete a QueryableList. Returns the value of a given field on an item

                @param item <???> - The item that needs a value fetched off it
                @param fieldName <str> - The name of the field on that item which is being requested

            @return - The value of the #fieldName attribute/key/whatever on #item

        '''
        raise NotImplementedError('QueryableList type must implement _get_item_value')


    def _getItemValueFunction(self, caches, _get_item_value):

        _i = ctypes.c_int()

        maxI = len(caches)

        def _getItemValue_impl(item, fieldName):
            i = _i.value
            cache = caches[i]
            _i.value += 1
            if i >= maxI:
                _i.value = 0
            else:
                _i.value = i

            if fieldName in cache:
                val = cache[fieldName]
            else:
                val = _get_item_value(item, fieldName)
                cache[fieldName] = val
            return val

        return _getItemValue_impl

    def customFilter(self, filterFunc):
        '''
            customFilter - Apply a custom filter to elements and return a QueryableList of matches

            @param filterFunc <lambda/function< - A lambda/function that is passed an item, and
               returns True if the item matches (will be returned), otherwise False.

            @return - A QueryableList object of the same type, with only the matching objects returned.
        '''
        ret = self.__class__()
        for item in self:
            if filterFunc(item):
                ret.append(item)

        return ret
                

    def count(self):
        '''
            count - Returns the number of items in this collection.

                This is the same as len(...), but is added to be compatible with many server-side ORMs which implement "count" as a function.

              @return <int> - Number of items in this collection
        '''
        return len(self)


    def sort_by(self, fieldName, reverse=False):
        '''
            sort_by - Return a copy of this collection, sorted by the given fieldName.

              The fieldName is accessed the same way as other filtering, so it supports custom properties, etc.

              @param fieldName <str> - The name of the field on which to sort by

              @param reverse <bool> Default False - If True, list will be in reverse order.

              @return <QueryableList> - A QueryableList of the same type with the elements sorted based on arguments.
        '''
        return self.__class__(
            sorted(self, key = lambda item : self._get_item_value(item, fieldName), reverse=reverse)
        )


    def filterAnd(self, **kwargs):
        '''
            filter/filterAnd - Performs a filter and returns a QueryableList object of the same type.

                All the provided filters must match for the item to be returned.

            @params are in the format of fieldName__operation=value  where fieldName is the name of the field on any given item, "operation" is one of the given operations (@see main documentation) (e.x. eq, ne, isnull), and value is what is used in the operation.

            @return - A QueryableList object of the same type, with only the matching objects returned.
        '''
        filters = getFiltersFromArgs(kwargs)
        ret = self.__class__()

        if USE_CACHED:
            caches = [dict() for i in range(len(self))]
            get_item_value = self._getItemValueFunction(caches, self._get_item_value)
        else:
            get_item_value = self._get_item_value

        # AND loop - for each item in this collection, run through each of the filter types.
        # If any of the filter types do not match, move on to next item
        # If all filters match, add item to the return set
        for item in self:
            keepIt = True

            # Do is/isnot first (and implicitly, isnull)
            for fieldName, value in filters['is']:
                if get_item_value(item, fieldName) is not value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['isnot']:
                if get_item_value(item, fieldName) is value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, matchFunc in filters['customMatch']:
                val = get_item_value(item, fieldName)
                if not matchFunc(val):
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['in']:
                if get_item_value(item, fieldName) not in value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['notin']:
                if get_item_value(item, fieldName) in value:
                    keepIt = False
                    break

            if keepIt is False:
                continue


            for fieldName, value in filters['eq']:
                if get_item_value(item, fieldName) != value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['ieq']:
                # If we can't lowercase the item's value, it obviously doesn't match whatever we previously could.
                # Reminder: the "i" filter's values have already been lowercased
                itemValue = get_item_value(item, fieldName)
                try:
                    itemValueLower = itemValue.lower()
                except:
                    keepIt = False
                    break

                if itemValueLower != value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['ne']:
                if get_item_value(item, fieldName) == value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['ine']:
                itemValue = get_item_value(item, fieldName)
                try:
                    itemValueLower = itemValue.lower()
                except:
                    # If we can't convert the field value to lowercase, it does not equal the other.
                    continue

                if itemValueLower == value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['lt']:
                if get_item_value(item, fieldName) >= value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['lte']:
                if get_item_value(item, fieldName) > value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['gt']:
                if get_item_value(item, fieldName) <= value:
                    keepIt = False
                    break

            if keepIt is False:
                continue


            for fieldName, value in filters['gte']:
                if get_item_value(item, fieldName) < value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['contains']:
                itemValue = get_item_value(item, fieldName)
                try:
                    if value not in itemValue:
                        keepIt = False
                        break
                except:
                    # If field does not support "in", it does not contain the item.
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['icontains']:
                itemValue = get_item_value(item, fieldName)
                try:
                    itemValue = itemValue.lower()

                    if value not in itemValue:
                        keepIt = False
                        break
                except:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['notcontains']:
                itemValue = get_item_value(item, fieldName)
                try:
                    if value in itemValue:
                        keepIt = False
                        break
                except:
                    # If field does not support "in", it does not contain the item.
                    continue

            if keepIt is False:
                continue

            for fieldName, value in filters['noticontains']:
                itemValue = get_item_value(item, fieldName)
                try:
                    itemValue = itemValue.lower()

                    if value in itemValue:
                        keepIt = False
                        break
                except:
                    continue


            if keepIt is False:
                continue

            for fieldName, value in filters['containsAny']:
                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split None
                    keepIt = False
                    break

                didContain = False
                for maybeContains in value:
                    if maybeContains in itemValue:
                        didContain = True
                        break
                if didContain is False:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['notcontainsAny']:
                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split None, so it is a match..
                    continue

                didContain = False
                for maybeContains in value:
                    if maybeContains in itemValue:
                        didContain = True
                        break
                if didContain is True:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            # IDEA: Could implement a dict here of last several splits, incase we have repeated splits on same large field.
            #   I think this may be more lossy in the general case to support a corner case though.

            for fieldName, value in filters['splitcontains']:
                (splitBy, maybeContains) = value

                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split, no match
                    keepIt = False
                    break

                try:
                    itemValue = itemValue.split(splitBy)
                    if maybeContains not in itemValue:
                        keepIt = False
                        break
                except:
                    # If field does not supprt "in", or cannot be split, it does not contain the item.
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['splitnotcontains']:
                (splitBy, maybeContains) = value

                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split, so does not contain and is a match.
                    continue

                try:
                    itemValue = itemValue.split(splitBy)
                    if maybeContains in itemValue:
                        keepIt = False
                        break
                except:
                    # If field does not supprt "in", or cannot be split, it does not contain the item and thus matches here.
                    continue

            if keepIt is False:
                continue

            for fieldName, value in filters['splitcontainsAny']:
                (splitBy, maybeContainsLst) = value

                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split, so it does not contain a match
                    keepIt = False
                    break

                try:
                    itemValue = itemValue.split(splitBy)
                except:
                    # Cannot split, does not match.
                    keepIt = False
                    break


                didContain = False
                for maybeContains in maybeContainsLst:
                    if maybeContains in itemValue:
                        didContain = True
                        break
                if didContain is False:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['splitnotcontainsAny']:
                (splitBy, maybeContainsLst) = value

                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split, so it must not contain any (and is a match)
                    continue

                try:
                    itemValue = itemValue.split(splitBy)
                except:
                    # Cannot split, so must not contain any (and is a match)
                    continue

                didContain = False
                for maybeContains in maybeContainsLst:
                    if maybeContains in itemValue:
                        didContain = True
                        break
                if didContain is True:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            # All the way through all filters, the item matches.
            ret.append(item)

        return ret


    '''
        filter - Synonym to '#filterAnd'

        @see #QueryableListBase.filterAnd
    '''
    filter = filterAnd

    def filterOr(self, **kwargs):
        '''
            filterOr - Performs a filter and returns a QueryableList object of the same type.

                Anythe provided filters can match for the item to be returned.

            @params are in the format of fieldName__operation=value  where fieldName is the name of the field on any given item, "operation" is one of the given operations (@see main documentation) (e.x. eq, ne, isnull), and value is what is used in the operation.

            @return - A QueryableList object of the same type, with only the matching objects returned.
        '''
        filters = getFiltersFromArgs(kwargs)
        ret = self.__class__()

        if USE_CACHED:
            caches = [dict() for i in range(len(self))]
            get_item_value = self._getItemValueFunction(caches, self._get_item_value)
        else:
            get_item_value = self._get_item_value

        # OR filtering - For each item in the collection
        #   Run through each filter type. If anything matches, we add the item to the collection and continue
        #   If we get to the end without a match, we continue to next item
        for item in self:
            keepIt = False

            # Do is/isnot (and implicitly isnull) first.
            for fieldName, value in filters['is']:
                if get_item_value(item, fieldName) is value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['isnot']:
                if get_item_value(item, fieldName) is not value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, matchFunc in filters['customMatch']:
                val = get_item_value(item, fieldName)
                if matchFunc(val):
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['in']:
                if get_item_value(item, fieldName) in value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['notin']:
                if get_item_value(item, fieldName) not in value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['eq']:
                if get_item_value(item, fieldName) == value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['ieq']:
                # If we can't lowercase the item's value, it obviously doesn't match whatever we previously could.
                # Reminder: the "i" filter's values have already been lowercased
                itemValue = get_item_value(item, fieldName)
                try:
                    itemValueLower = itemValue.lower()
                except:
                    keepIt = False
                    break

                if itemValueLower == value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['ne']:
                if get_item_value(item, fieldName) != value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['ine']:
                itemValue = get_item_value(item, fieldName)
                try:
                    itemValueLower = itemValue.lower()
                except:
                    # If we can't convert the field value to lowercase, it does not equal the other.
                    continue

                if itemValueLower != value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['lt']:
                if get_item_value(item, fieldName) < value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['lte']:
                if get_item_value(item, fieldName) <= value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['gt']:
                if get_item_value(item, fieldName) > value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue


            for fieldName, value in filters['gte']:
                if get_item_value(item, fieldName) >= value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['contains']:
                itemValue = get_item_value(item, fieldName)
                try:
                    if value in itemValue:
                        keepIt = True
                        break
                except:
                    # If field does not support "in", it does not contain the item.
                    continue

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['icontains']:
                itemValue = get_item_value(item, fieldName)
                try:
                    itemValue = itemValue.lower()

                    if value in itemValue:
                        keepIt = True
                        break
                except:
                    continue

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['notcontains']:
                itemValue = get_item_value(item, fieldName)
                try:
                    if value not in itemValue:
                        keepIt = True
                        break
                except:
                    # If field does not support "in", it does not contain the item.
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['noticontains']:
                itemValue = get_item_value(item, fieldName)
                try:
                    itemValue = itemValue.lower()

                    if value not in itemValue:
                        keepIt = True
                        break
                except:
                    # If field does not support "in", it does not contain the item.
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue


            for fieldName, value in filters['containsAny']:
                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # None contains nothing, no match
                    continue

                didContain = False
                for maybeContains in value:
                    if maybeContains in itemValue:
                        didContain = True
                        break
                if didContain is True:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['notcontainsAny']:
                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # None contains nothing, so this is a match
                    keepIt = True
                    break

                didContain = False
                for maybeContains in value:
                    if maybeContains in itemValue:
                        didContain = True
                        break
                if didContain is False:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue


            for fieldName, value in filters['splitcontains']:
                (splitBy, maybeContains) = value

                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split, no match
                    continue

                try:
                    itemValue = itemValue.split(splitBy)
                    if maybeContains in itemValue:
                        keepIt = True
                        break
                except:
                    # If field does not supprt "in", or cannot be split, it does not contain the item.
                    continue


            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['splitnotcontains']:
                (splitBy, maybeContains) = value

                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split, so does not contain and is a match.
                    keepIt = True
                    break


                try:
                    itemValue = itemValue.split(splitBy)
                    if maybeContains not in itemValue:
                        keepIt = True
                        break
                except:
                    # If field does not supprt "in", or cannot be split, it does not contain the item and thus matches here.
                    keepIt = True
                    break


            if keepIt is True:
                ret.append(item)
                continue


            for fieldName, value in filters['splitcontainsAny']:
                (splitBy, maybeContainsLst) = value

                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split, so it does not contain a match
                    continue

                try:
                    itemValue = itemValue.split(splitBy)
                except:
                    # Cannot split, does not match.
                    continue


                didContain = False
                for maybeContains in maybeContainsLst:
                    if maybeContains in itemValue:
                        didContain = True
                        break

                if didContain is True:
                    keepIt = True
                    break


            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['splitnotcontainsAny']:
                (splitBy, maybeContainsLst) = value

                itemValue = get_item_value(item, fieldName)

                if itemValue is None:
                    # Cannot split, so it must not contain any (and is a match)
                    keepIt = True
                    break

                try:
                    itemValue = itemValue.split(splitBy)
                except:
                    # Cannot split, so must not contain any (and is a match)
                    keepIt = True
                    break

                didContain = False
                for maybeContains in maybeContainsLst:
                    if maybeContains in itemValue:
                        didContain = True
                        break
                if didContain is False:
                    keepIt = True
                    break


            if keepIt is True:
                ret.append(item)
                continue


        return ret

    ################################################
    ##     List overrides to return same type     ##
    ################################################

    def __add__(self, other):
        '''
            __add__ - Append all items in #other to the tail of #self

                + operator

              Returns a copy, does not modify this item.
        '''
        return self.__class__(list.__add__(self, other))

    def __iadd__(self, other):
        '''
            __iadd__ - Append all items in #other to the tail of #self

              += operator

              Modifies original

        '''
        list.__iadd__(self, other)
        return self

    def __getslice__(self, start, end):
        '''
            __getslice__ - Return a "slice" (subset) of the current collection.

            Returns a copy
        '''
        return self.__class__(list.__getslice__(self, start, end))

    def __repr__(self):
        '''
            __repr__ - Return a code representation of this class
        '''
        return "%s(%s)" %(self.__class__.__name__, list.__repr__(self))

    ################################################
    ##     Extras that list doesn't support       ##
    ################################################

    def __sub__(self, other):
        '''
            __sub__ - Implement subtract. Removes any items from #self that are present in #other

              Returns a copy, does not modify inline
        '''
        myCopy = self[:]

        for item in other:
            while True:
                # Remove ALL copies
                try:
                    myCopy.remove(item)
                except ValueError:
                    break
        return myCopy

    def __isub__(self, other):
        '''
            __isub__ - Implement subtract-equals. Removes any items from #self that are present in #other

            Works inline and modifies #self
        '''
        for item in other:
            while True:
                # Remove ALL copies of OTHER
                try:
                    self.remove(item)
                except ValueError:
                    break

        return self



    def __or__(self, other):
        '''
            __or__ - Append any items found in #other which are not already present in #self

                Returns a copy
        '''
        ret = self[:]
        for item in other:
            if item not in self:
                ret.append(item)

        return ret

    def __ior__(self, other):
        for item in other:
            if item not in self:
                self.append(item)
        return self

    def __and__(self, other):
        '''
            __and__ - Return a QueryableList (of this type) which contains all the elements in #self that are also in #other

              Returns a copy
        '''
        # TODO: Optimize for least number of searches, N > M stuff
        ret = self.__class__([])
        for item in self:
            if item in other:
                ret.append(item)

        return ret

    def __iand__(self, other):
        for item in self:
            if item not in other:
                self.remove(item)
        return self

    def __xor__(self, other):
        '''
            __xor__ - Return a QueryableList (of this type) which contains all the elements
              that appear in either #self or #other, but not both.

              Returns a copy
        '''
        ret = self[:]
        for item in other:
            if item not in self:
                ret.append(item)
            else:
                ret.remove(item)

        return ret

    def __ixor__(self, other):
        for item in other:
            if item not in self:
                self.append(item)
            else:
                self.remove(item)
        return self

    def __copy__(self):
        '''
            __copy__ - Make a copy of this collection
        '''
        return self.__class__(self)



#vim: set ts=4 st=4 sw=4 expandtab
