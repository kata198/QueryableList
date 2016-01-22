
# FILTER_TYPES - All available filter types
FILTER_TYPES = {'eq', 'ieq', 'ne', 'ine', 'lt', 'gt', 'lte', 'gte', 'isnull', 'is', 'isnot', 
    'in', 'notin', 'contains', 'notcontains', 'containsAny', 'notcontainsAny',
    'splitcontains', 'splitnotcontains', 'splitcontainsAny', 'splitnotcontainsAny'}


FILTER_METHOD_AND = 'AND'
FILTER_METHOD_OR  = 'OR'

# FILTER_METHODS - Possible methods for filtering
FILTER_METHODS = (FILTER_METHOD_AND, FILTER_METHOD_OR)
