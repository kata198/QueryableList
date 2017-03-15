# Copyright (c) 2016, 2017 Timothy Savannah under the terms of the GNU Lesser General Public License version 2.1.
#  You should have received a copy of this as "LICENSE" with this source distribution. The full license is available at https://raw.githubusercontent.com/kata198/QueryableList/master/LICENSE
from .constants import FILTER_TYPES

import re

__all__ = ('FILTER_PARAM_RE', 'getFiltersFromArgs', 'QueryableListBase')

FILTER_PARAM_RE = re.compile('^(?P<field>.+)__(?P<filterType>.+)$')


def getFiltersFromArgs(kwargs):
    '''
        getFiltersFromArgs - Returns a dictionary of each filter type, and the corrosponding field/value

        @param kwargs <dict> - Dictionary of filter arguments


        @return - Dictionary of each filter type (minus the ones that are optimized into others), each containing a list of tuples, (fieldName, matchingValue)
    '''

    # Hard copy of FILTER_TYPES here for optimization/reworking. 
    ret = {
        'eq'       : [],
        'ieq'      : [],
        'ne'       : [],
        'ine'      : [],
        'lt'       : [],
        'gt'       : [],
        'lte'      : [],
        'gte'      : [],
        'is'       : [],
        'isnot'    : [],
        'in'       : [],
        'notin'    : [],
        'contains' : [],
        'icontains': [],
        'notcontains' : [],
        'noticontains' : [],
        'containsAny' : [],
        'notcontainsAny' : [],
        'splitcontains' : [],
        'splitnotcontains' : [],
        'splitcontainsAny' : [],
        'splitnotcontainsAny' : [],
    }

    for key, value in kwargs.items():
        matchObj = FILTER_PARAM_RE.match(key)
        if not matchObj:

            # Default is eq
            filterType = 'eq'
            field = key

        else:

            groupDict = matchObj.groupdict()

            filterType = groupDict['filterType']
            field = groupDict['field']


            if filterType not in FILTER_TYPES:
                raise ValueError('Unknown filter type: %s. Choices are: (%s)' %(filterType, ', '.join(FILTER_TYPES)))


            if filterType == 'isnull':
                # Convert "isnull" to one of the "is" or "isnot" filters
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
        return self


    @staticmethod
    def _get_item_value(item, fieldName):
        '''
            _get_item_value - Must be implemented to complete a QueryableList. Returns the value of a given field on an item

                @param item <???> - The item that needs a value fetched off it
                @param fieldName <str> - The name of the field on that item which is being requested

            @return - The value of the #fieldName attribute/key/whatever on #item

        '''
        raise NotImplementedError('QueryableList type must implement _get_item_value')


    def filterAnd(self, **kwargs):
        '''
            filter/filterAnd - Performs a filter and returns a QueryableList object of the same type.

                All the provided filters must match for the item to be returned.

            @params are in the format of fieldName__operation=value  where fieldName is the name of the field on any given item, "operation" is one of the given operations (@see main documentation) (e.x. eq, ne, isnull), and value is what is used in the operation.

            @return - A QueryableList object of the same type, with only the matching objects returned.
        '''
        filters = getFiltersFromArgs(kwargs)
        ret = self.__class__()

        for item in self:
            keepIt = True

            # Do is/isnot first (and implicitly, isnull)
            for fieldName, value in filters['is']:
                if self._get_item_value(item, fieldName) is not value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['isnot']:
                if self._get_item_value(item, fieldName) is value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['in']:
                if self._get_item_value(item, fieldName) not in value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['notin']:
                if self._get_item_value(item, fieldName) in value:
                    keepIt = False
                    break

            if keepIt is False:
                continue


            for fieldName, value in filters['eq']:
                if self._get_item_value(item, fieldName) != value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['ieq']:
                # If we can't lowercase the item's value, it obviously doesn't match whatever we previously could.
                # Reminder: the "i" filter's values have already been lowercased
                itemValue = self._get_item_value(item, fieldName)
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
                if self._get_item_value(item, fieldName) == value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['ine']:
                itemValue = self._get_item_value(item, fieldName)
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
                if self._get_item_value(item, fieldName) >= value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['lte']:
                if self._get_item_value(item, fieldName) > value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['gt']:
                if self._get_item_value(item, fieldName) <= value:
                    keepIt = False
                    break

            if keepIt is False:
                continue


            for fieldName, value in filters['gte']:
                if self._get_item_value(item, fieldName) < value:
                    keepIt = False
                    break

            if keepIt is False:
                continue

            for fieldName, value in filters['contains']:
                itemValue = self._get_item_value(item, fieldName)
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
                itemValue = self._get_item_value(item, fieldName)
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
                itemValue = self._get_item_value(item, fieldName)
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
                itemValue = self._get_item_value(item, fieldName)
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
                itemValue = self._get_item_value(item, fieldName)

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
                itemValue = self._get_item_value(item, fieldName)

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

                itemValue = self._get_item_value(item, fieldName)

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

                itemValue = self._get_item_value(item, fieldName)

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

                itemValue = self._get_item_value(item, fieldName)

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

                itemValue = self._get_item_value(item, fieldName)

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

        for item in self:
            keepIt = False

            # Do is/isnot (and implicitly isnull) first.
            for fieldName, value in filters['is']:
                if self._get_item_value(item, fieldName) is value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['isnot']:
                if self._get_item_value(item, fieldName) is not value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['in']:
                if self._get_item_value(item, fieldName) in value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['notin']:
                if self._get_item_value(item, fieldName) not in value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['eq']:
                if self._get_item_value(item, fieldName) == value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['ieq']:
                # If we can't lowercase the item's value, it obviously doesn't match whatever we previously could.
                # Reminder: the "i" filter's values have already been lowercased
                itemValue = self._get_item_value(item, fieldName)
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
                if self._get_item_value(item, fieldName) != value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['ine']:
                itemValue = self._get_item_value(item, fieldName)
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
                if self._get_item_value(item, fieldName) < value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['lte']:
                if self._get_item_value(item, fieldName) <= value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['gt']:
                if self._get_item_value(item, fieldName) > value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue


            for fieldName, value in filters['gte']:
                if self._get_item_value(item, fieldName) >= value:
                    keepIt = True
                    break

            if keepIt is True:
                ret.append(item)
                continue

            for fieldName, value in filters['contains']:
                itemValue = self._get_item_value(item, fieldName)
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
                itemValue = self._get_item_value(item, fieldName)
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
                itemValue = self._get_item_value(item, fieldName)
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
                itemValue = self._get_item_value(item, fieldName)
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
                itemValue = self._get_item_value(item, fieldName)

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
                itemValue = self._get_item_value(item, fieldName)

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

                itemValue = self._get_item_value(item, fieldName)

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

                itemValue = self._get_item_value(item, fieldName)

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

                itemValue = self._get_item_value(item, fieldName)

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

                itemValue = self._get_item_value(item, fieldName)

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
        return self.__class__(list.__add__(self, other))

    def __iadd__(self, other):
        return self.__class__(list.__iadd__(self, other))

    def __getslice__(self, start, end):
        return self.__class__(list.__getslice__(self, start, end))

    def __repr__(self):
        return "%s(%s)" %(self.__class__.__name__, list.__repr__(self))

    ################################################
    ##     Extras that list doesn't support       ##
    ################################################

    def __sub__(self, other):
        myCopy = self[:]
        for item in other:
            try:
                myCopy.remove(item)
            except:
                pass
        return myCopy

    def __or__(self, other):
        ret = self[:]
        for item in other:
            if item not in self:
                ret.append(item)

        return ret

    def __and__(self, other):
        ret = self.__class__([])
        for item in self:
            if item in other:
                ret.append(item)

        return ret


    def __xor__(self, other):
        ret = self[:]
        for item in other:
            if item not in self:
                ret.append(item)
            else:
                ret.remove(item)

        return ret


