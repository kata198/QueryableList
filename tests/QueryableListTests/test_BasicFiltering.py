#!/usr/bin/env GoodTests.py

import sys
import subprocess

from QueryableList import QueryableListObjs, QueryableListDicts, QueryableListMixed


class DataObject(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class TestBasicFiltering(object):

    def setup_class(self):
        self.dataObjs = [
            DataObject(a='one', b='two'),
            DataObject(a='one', b='five'),
            DataObject(a='six', c='eleven'),
        ]

        self.dataDicts = [ 
            { 'a' : 'one', 'b' : 'two'}, 
            { 'a' : 'one', 'b' : 'five'}, 
            { 'a' : 'six', 'c' : 'eleven'},
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

if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait())
