#!/usr/bin/env GoodTests.py

# vim: set ts=4 st=4 sw=4 expandtab :

import sys
import subprocess

from QueryableList import QueryableListObjs, QueryableListDicts, QueryableListMixed


class DataObject(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class TestQueryableListTypes(object):

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


    def test_Objs(self):

        gotException = False

        try:
            qlObjs = QueryableListObjs(self.dataObjs)
            found = qlObjs.filter(a='one')
        except Exception as e:
            gotException = e

        assert gotException is False, 'Got Exception for QueryableListObjs when should not have: %s%s' %(str(type(e)), str(e)) 
        assert len(found) == 2, 'Did not find correct number of items'

        gotException = False
        try:
            dObjs = QueryableListObjs(self.dataDicts)
            found = dObjs.filter(a='one')
        except Exception as e:
            # I personally think this should raise an exception, so test is written like this,
            #  but it would be too performant loss to check every time.
            gotException = e

        #assert gotException is not False, 'Expected to get exception, but did not.'
        assert len(found) == 0, 'Expected not to find any items when using QueryableListObjs with list of dicts'

    def test_Dicts(self):

        gotException = False

        try:
            qlDicts = QueryableListDicts(self.dataDicts)
            found = qlDicts.filter(a='one')
        except Exception as e:
            gotException = e

        assert gotException is False, 'Got Exception for QueryableListDicts when should not have: %s%s' %(str(type(e)), str(e)) 
        assert len(found) == 2, 'Did not find correct number of items'

        gotException = False
        try:
            dDicts = QueryableListObjs(self.dataDicts)
            found = dDicts.filter(a='one')
        except Exception as e:
            # I personally think this should raise an exception, so test is written like this,
            #  but it would be too performant loss to check every time.
            gotException = e

        #assert gotException is not False, 'Expected to get exception, but did not.'
        assert len(found) == 0, 'Expected not to find any items when using QueryableListDicts with list of objs'


    def testMixed(self):
        gotException = False

        try:
            qlDicts = QueryableListMixed(self.dataDicts)
            found = qlDicts.filter(a='one')
        except Exception as e:
            gotException = e

        assert gotException is False, 'Got Exception for QueryableListMixed on objects when should not have: %s%s' %(str(type(e)), str(e)) 
        assert len(found) == 2, 'Did not find correct number of items'

        gotException = False
        try:
            dDicts = QueryableListMixed(self.dataDicts)
            found = dDicts.filter(a='one')
        except Exception as e:
            gotException = e

        assert gotException is False, 'Got Exception for QueryableListMixed on dicts when should not have: %s%s' %(str(type(e)), str(e)) 
        assert len(found) == 2, 'Did not find correct number of items'




if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())

# vim: set ts=4 st=4 sw=4 expandtab :
