# Copyright (c) 2016, 2017 Timothy Savannah under the terms of the GNU Lesser General Public License version 2.1.
#  You should have received a copy of this as "LICENSE" with this source distribution. The full license is available at https://raw.githubusercontent.com/kata198/QueryableList/master/LICENSE

# FILTER_TYPES - All available filter types
FILTER_TYPES = {'eq', 'ieq', 'ne', 'ine', 'lt', 'gt', 'lte', 'gte', 'isnull', 'is', 'isnot', 
    'in', 'notin', 'contains', 'icontains', 'notcontains', 'noticontains', 'containsAny', 'notcontainsAny',
    'splitcontains', 'splitnotcontains', 'splitcontainsAny', 'splitnotcontainsAny'}


FILTER_METHOD_AND = 'AND'
FILTER_METHOD_OR  = 'OR'

# FILTER_METHODS - Possible methods for filtering
FILTER_METHODS = (FILTER_METHOD_AND, FILTER_METHOD_OR)
