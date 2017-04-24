#!/usr/bin/env GoodTests.py

# vim: set ts=4 st=4 sw=4 expandtab :
''' 
    Test for all operations.

    TODO: Test all operations

'''

import sys
import subprocess

from QueryableList import QueryableListObjs, QueryableListDicts, QueryableListMixed

from tutils import filterDictToStr, DataObject


class TestOperations(object):

    def setup_class(self):
        self.dataObjs = [
            DataObject(a='one', b='two', null1=None, emptyStr='', q='cheese', num=7),
            DataObject(a='one', b='five', null1=None, emptyStr='', q='cheese', num=-5),
            DataObject(a='six', c='eleven', null1=None, emptyStr='', q='bacon', num=7),
        ]

        self.dataDicts = [ 
            { 'a' : 'one', 'b' : 'two', 'null1' : None, 'emptyStr' : '', 'q' : 'cheese', 'num' : 7}, 
            { 'a' : 'one', 'b' : 'five', 'null1' : None, 'emptyStr' : '', 'q' : 'cheese', 'num' : -5},
            { 'a' : 'six', 'c' : 'eleven', 'null1' : None, 'emptyStr' : '', 'q' : 'bacon', 'num' : 7},
        ]


    @staticmethod
    def _filterDictToStr(filterDict):
        return ', '.join(['%s=%s' %(key, repr(value)) for key, value in filterDict.items()])

    def _doTest(self, qlObjs, filterType, filterDict, expectedObjs):
        filterType = filterType.upper()

        if filterType == 'AND':
            filterMethod = qlObjs.filterAnd
        elif filterType == 'OR':
            filterMethod = qlObjs.filterOr
        else:
            raise ValueError('Unknown filter type: %s' %(filterType, ))

        results = filterMethod(**filterDict)


        resultsSet = set(results)
        expectedObjsSet = set(expectedObjs)

        missingItems = expectedObjsSet - resultsSet

        try:
            assert not missingItems
        except AssertionError as e:
            raise AssertionError('Missing expected item%s in %s query { %s }: %s' %(len(missingItems) > 1 and 's' or '', filterType, filterDictToStr(filterDict), str(list(missingItems))) )


        extraItems = resultsSet - expectedObjsSet
        
        try:
            assert not extraItems
        except AssertionError as e:
            raise AssertionError('Got unexpected item%s in %s query { %s }: %s' %(len(extraItems) > 1 and 's' or '', filterType, filterDictToStr(filterDict), str(list(extraItems))) )

        # Should never be true... but I wanted the verbose results above so I moved this test down
        try:
            assert len(results) == len(expectedObjs)
        except AssertionError as e:
            raise AssertionError('Expected %s query { %s } to return %d objects. Got: %d' %(filterType, filterDictToStr(filterDict), len(expectedObjs), len(results)) )
        
        return True # cuz... why not?

    def test_eq(self):
        # Test __eq and = both
        dataObjs = self.dataObjs
        doTest = self._doTest

        qlObjs = QueryableListObjs(dataObjs)


        doTest(qlObjs, 'AND', {'a' : 'six'}, (dataObjs[2], ))
        doTest(qlObjs, 'AND', {'a__eq' : 'six'}, (dataObjs[2], ))
        doTest(qlObjs, 'AND', {'a' : 'one'}, (dataObjs[0], dataObjs[1] ))
        doTest(qlObjs, 'AND', {'a' : 'one', 'emptyStr' : ''}, (dataObjs[0], dataObjs[1] ))
        doTest(qlObjs, 'AND', {'a' : 'one', 'q' : 'cheese'}, (dataObjs[0], dataObjs[1] ))
        doTest(qlObjs, 'AND', {'emptyStr' : '', 'num__eq' : 7}, (dataObjs[0], dataObjs[2] ))

        doTest(qlObjs, 'OR', {'a' : 'six'}, (dataObjs[2], ))
        doTest(qlObjs, 'OR', {'a__eq' : 'six'}, (dataObjs[2], ))
        doTest(qlObjs, 'OR', {'a' : 'one', 'q__eq' : 'bacon'}, (dataObjs[0], dataObjs[1], dataObjs[2] ))
        doTest(qlObjs, 'OR', {'a' : 'one', 'emptyStr' : ''}, (dataObjs[0], dataObjs[1], dataObjs[2] ))
        doTest(qlObjs, 'OR', {'a' : 'six', 'num__eq' : 7}, (dataObjs[0], dataObjs[2] ))

#        self.dataDicts = [ 
#            { 'a' : 'one', 'b' : 'two', 'null1' : None, 'emptyStr' : '', 'q' : 'cheese', 'num' : 7}, 
#            { 'a' : 'one', 'b' : 'five', 'null1' : None, 'emptyStr' : '', 'q' : 'cheese', 'num' : -5},
#            { 'a' : 'six', 'c' : 'eleven', 'null1' : None, 'emptyStr' : '', 'q' : 'bacon', 'num' : 7},
#        ]

    def test_ne(self):
        dataObjs = self.dataObjs
        doTest = self._doTest

        qlObjs = QueryableListObjs(dataObjs)

        doTest(qlObjs, 'AND', {'a__ne' : 'six'}, (dataObjs[0], dataObjs[1] ))
        doTest(qlObjs, 'AND', {'a__ne' : 'five'}, (dataObjs[0], dataObjs[1], dataObjs[2] ))
        doTest(qlObjs, 'AND', {'num__ne' : -5, 'a__ne' : 'one'}, (dataObjs[2], ) )
        doTest(qlObjs, 'AND', {'num__ne' : -5, 'a__ne' : 'six'}, (dataObjs[0], ) )

        doTest(qlObjs, 'OR', {'a__ne' : 'one', 'q__ne' : 'cheese'}, (dataObjs[2], ))
        doTest(qlObjs, 'OR', {'a__ne' : 'six', 'num__ne' : -5}, (dataObjs[0], dataObjs[1], dataObjs[2] ) )


    def text_mixed(self):
        dataObjs = self.dataObjs
        doTest = self._doTest

        qlObjs = QueryableListObjs(dataObjs)

        doTest(qlObjs, 'AND', {'a__eq' : 'six', 'num__ne' : 7}, tuple() )
        doTest(qlObjs, 'AND', {'a__eq' : 'one', 'num__ne' : 7}, tuple(dataObjs[1]) )

    def test_customMatch(self):
        dataObjs = self.dataObjs
        doTest = self._doTest

        qlObjs = QueryableListObjs(dataObjs)

        doTest(qlObjs, 'AND', {'q__customMatch' : lambda q : q and len(q) > 5 }, (dataObjs[0], dataObjs[1]) )

    def test_customFilter(self):
        dataObjs = self.dataObjs
        doTest = self._doTest

        qlObjs = QueryableListObjs(dataObjs)

        matchFunc = lambda item : getattr(item, 'b', None) and item.num > 0

        results = qlObjs.customFilter(matchFunc)

        assert len(results) == 1 , 'Expected to get one result, got %d' %(len(results),)

        assert results[0] == dataObjs[0]

        matchFunc = lambda item : item.a.upper() == 'ONE'

        results = qlObjs.customFilter(matchFunc)

        assert len(results) == 2, 'Expected to get two results, got %d' %(len(results),)

        assert dataObjs[0] in results, 'Expected dataObjs[0] to be in match'
        assert dataObjs[1] in results, 'Expected dataObjs[1] to be in match'


        
if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())

# vim: set ts=4 st=4 sw=4 expandtab :
