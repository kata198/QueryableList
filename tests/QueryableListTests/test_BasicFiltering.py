#!/usr/bin/env GoodTests.py

# vim: set ts=4 st=4 sw=4 expandtab :
''' 
    Some basic sanity tests that filtering is working

'''

import sys
import subprocess

from QueryableList import QueryableListObjs, QueryableListDicts, QueryableListMixed

from tutils import DataObject

class TestBasicFiltering(object):

    def setup_class(self):
        self.dataObjs = [
            DataObject(a='one', b='two', null1=None, emptyStr=''),
            DataObject(a='one', b='five', null1=None, emptyStr=''),
            DataObject(a='six', c='eleven', null1=None, emptyStr=''),
        ]

        self.dataDicts = [ 
            { 'a' : 'one', 'b' : 'two', 'null1' : None, 'emptyStr' : ''}, 
            { 'a' : 'one', 'b' : 'five', 'null1' : None, 'emptyStr' : ''},
            { 'a' : 'six', 'c' : 'eleven', 'null1' : None, 'emptyStr' : ''},
        ]


    def test_equals(self):
        # Test __eq and = both
        qlObjs = QueryableListObjs(self.dataObjs)

        found = qlObjs.filter(a='six')

        assert len(found) == 1, 'Expected to find one item in query(=), found %d' %(len(found), )

        assert found[0].a == 'six' and found[0].c == 'eleven', 'Found wrong item from equals query'

        found = qlObjs.filter(a__eq='six')
        assert len(found) == 1, 'Expected to find one item in query(__eq), found %d' %(len(found), )

        assert found[0].a == 'six' and found[0].c == 'eleven', 'Found wrong item from equals query'

        found = QueryableListObjs(self.dataObjs).filter(a__eq='one')

        assert len(found) == 2, 'Expected to find two items in query, found %d' %(len(found), )

    def test_ne(self):
        qlObjs = QueryableListObjs(self.dataObjs)

        found = qlObjs.filter(a__ne='one')

        assert len(found) == 1, 'Expected to find one item in query, found %d' %(len(found), )

        assert found[0].a == 'six' and found[0].c == 'eleven', 'Found wrong item from equals query'

    def test_chaining(self):
        qlObjs = QueryableListObjs(self.dataObjs)

        found = qlObjs.filter(a__eq='one').filter(b__eq='two')

        assert len(found) == 1, 'Expected chained filter to return one element, got %d' %(len(found), )


        assert found[0].a == 'one' and found[0].b == 'two' , 'Got wrong item in chained query'

    def test_filterOr(self):
        qlObjs = QueryableListObjs(self.dataObjs)

        found = qlObjs.filterOr(a='six', b='five')

        assert len(found) == 2, 'Expected "or" filter to return 2 items for a="6" and b="five". Got: %s\n' %(str(found), )

        assert ( (found[0].a == 'six' or found[0].b == 'five') or (found[1].a == 'six' or found[1].b == 'five') ) , 'Got wrong items for a="6" and b="five". Got: %s' %(str(found),)

if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait())

# vim: set ts=4 st=4 sw=4 expandtab :
