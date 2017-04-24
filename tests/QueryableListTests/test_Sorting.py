#!/usr/bin/env GoodTests.py

# vim: set ts=4 st=4 sw=4 expandtab :
''' 
    Test sorting functionality

'''

import copy
import sys
import subprocess

from QueryableList import QueryableListObjs, QueryableListDicts, QueryableListMixed

from tutils import DataObject

class TestSorting(object):

    def setup_method(self, testFunc):

        self.dataObjs = [
            DataObject(a=1, b='aaa', null1=None, emptyStr=''),
            DataObject(a=9, b='bbb', null1=None, emptyStr=''),
            DataObject(a=7, b='aba', null1=None, emptyStr=''),
            DataObject(a=4, b='ccc', null1=None, emptyStr=''),
        ]

        self.dataDicts = [ 
            { 'a' : 1, 'b' : 'aaa', 'null1' : None, 'emptyStr' : ''}, 
            { 'a' : 9, 'b' : 'bbb', 'null1' : None, 'emptyStr' : ''},
            { 'a' : 7, 'b' : 'aba', 'null1' : None, 'emptyStr' : ''},
            { 'a' : 4, 'b' : 'ccc', 'null1' : None, 'emptyStr' : ''},
        ]

        self.dataObjsCopy = self.dataObjs[:]
        self.dataDictsCopy = copy.copy(self.dataDicts)

    @staticmethod
    def _get_list_of_values(lst, key):
        return [ getattr(x, key) for x in lst ]


    def test_sortObjsByInt(self):

        dataObjs = self.dataObjs

        qlObjs = QueryableListObjs(self.dataObjs)

        sortedByA = qlObjs.sort_by('a')

        sortedByAList = list(sortedByA)

        expectedList = [ dataObjs[0], dataObjs[3], dataObjs[2], dataObjs[1] ]

        assert sortedByAList == expectedList , 'Sort by field "a" failed to return expected order.\nGot:      %s\nExpected: %s\n' %( repr(self._get_list_of_values(sortedByAList, 'a')), repr( self._get_list_of_values(expectedList, 'a')) )

        assert dataObjs == self.dataObjsCopy , 'Expected sort_by to not modify original list'

        assert isinstance(sortedByA, QueryableListObjs) , 'Expected return to be a QueryableListObjs instance. Got: %s' %(sortedByA.__class__.__name__, )


        sortedByARev = qlObjs.sort_by('a', reverse=True)
        sortedByARevList = list(sortedByARev)

        expectedRevList = list(reversed(expectedList))

        assert sortedByARevList == expectedRevList , 'Reverse sort by field "a" failed to return expected order.\nGot:      %s\nExpected: %s\n' %( repr(self._get_list_of_values(sortedByARevList, 'a')), repr(self._get_list_of_values(expectedRevList, 'a')) )

        assert dataObjs == self.dataObjsCopy , 'Expected sort_by to not modify original list'

        assert isinstance(sortedByARev, QueryableListObjs) , 'Expected return to be a QueryableListObjs instance. Got: %s' %(sortedByARev.__class__.__name__, )

    def test_sortObjsByStr(self):
        dataObjs = self.dataObjs

        qlObjs = QueryableListObjs(self.dataObjs)

        sortedByB = qlObjs.sort_by('b')

        sortedByBList = list(sortedByB)

        expectedList = [ dataObjs[0], dataObjs[2], dataObjs[1], dataObjs[3] ]

        assert sortedByBList == expectedList , 'Sort by field "a" failed to return expected order.\nGot:      %s\nExpected: %s\n' %( repr(self._get_list_of_values(sortedByBList, 'b')), repr( self._get_list_of_values(expectedList, 'b')) )

        assert dataObjs == self.dataObjsCopy , 'Expected sort_by to not modify original list'

        assert isinstance(sortedByB, QueryableListObjs) , 'Expected return to be a QueryableListObjs instance. Got: %s' %(sortedByB.__class__.__name__, )


        sortedByBRev = qlObjs.sort_by('b', reverse=True)
        sortedByBRevList = list(sortedByBRev)

        expectedRevList = list(reversed(expectedList))

        assert sortedByBRevList == expectedRevList , 'Reverse sort by field "a" failed to return expected order.\nGot:      %s\nExpected: %s\n' %( repr(self._get_list_of_values(sortedByBRevList, 'b')), repr(self._get_list_of_values(sortedByBRevList, expectedRevList)) )

        assert dataObjs == self.dataObjsCopy , 'Expected sort_by to not modify original list'

        assert isinstance(sortedByBRev, QueryableListObjs) , 'Expected return to be a QueryableListObjs instance. Got: %s' %(sortedByBRev.__class__.__name__, )


    def test_sortDictsByInt(self):

        dataDicts = self.dataDicts

        qlDicts = QueryableListDicts(self.dataDicts)

        sortedByA = qlDicts.sort_by('a')

        sortedByAList = list(sortedByA)

        expectedList = [ dataDicts[0], dataDicts[3], dataDicts[2], dataDicts[1] ]

        assert sortedByAList == expectedList , 'Sort by field "a" failed to return expected order.\nGot:      %s\nExpected: %s\n' %( repr(self._get_list_of_values(sortedByAList, 'a')), repr( self._get_list_of_values(expectedList, 'a')) )

        assert dataDicts == self.dataDictsCopy , 'Expected sort_by to not modify original list'

        assert isinstance(sortedByA, QueryableListDicts) , 'Expected return to be a QueryableListDicts instance. Got: %s' %(sortedByA.__class__.__name__, )


        sortedByARev = qlDicts.sort_by('a', reverse=True)
        sortedByARevList = list(sortedByARev)

        expectedRevList = list(reversed(expectedList))

        assert sortedByARevList == expectedRevList , 'Reverse sort by field "a" failed to return expected order.\nGot:      %s\nExpected: %s\n' %( repr(self._get_list_of_values(sortedByARevList, 'a')), repr(self._get_list_of_values(expectedRevList, 'a')) )

        assert dataDicts == self.dataDictsCopy , 'Expected sort_by to not modify original list'

        assert isinstance(sortedByARev, QueryableListDicts) , 'Expected return to be a QueryableListDicts instance. Got: %s' %(sortedByARev.__class__.__name__, )

    def test_sortDictsByStr(self):
        dataDicts = self.dataDicts

        qlDicts = QueryableListDicts(self.dataDicts)

        sortedByB = qlDicts.sort_by('b')

        sortedByBList = list(sortedByB)

        expectedList = [ dataDicts[0], dataDicts[2], dataDicts[1], dataDicts[3] ]

        assert sortedByBList == expectedList , 'Sort by field "a" failed to return expected order.\nGot:      %s\nExpected: %s\n' %( repr(self._get_list_of_values(sortedByBList, 'b')), repr( self._get_list_of_values(expectedList, 'b')) )

        assert dataDicts == self.dataDictsCopy , 'Expected sort_by to not modify original list'

        assert isinstance(sortedByB, QueryableListDicts) , 'Expected return to be a QueryableListDicts instance. Got: %s' %(sortedByB.__class__.__name__, )


        sortedByBRev = qlDicts.sort_by('b', reverse=True)
        sortedByBRevList = list(sortedByBRev)

        expectedRevList = list(reversed(expectedList))

        assert sortedByBRevList == expectedRevList , 'Reverse sort by field "a" failed to return expected order.\nGot:      %s\nExpected: %s\n' %( repr(self._get_list_of_values(sortedByBRevList, 'b')), repr(self._get_list_of_values(sortedByBRevList, expectedRevList)) )

        assert dataDicts == self.dataDictsCopy , 'Expected sort_by to not modify original list'

        assert isinstance(sortedByBRev, QueryableListDicts) , 'Expected return to be a QueryableListDicts instance. Got: %s' %(sortedByBRev.__class__.__name__, )


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())

# vim: set ts=4 st=4 sw=4 expandtab :
