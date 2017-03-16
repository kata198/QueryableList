#!/usr/bin/env GoodTests.py
''' 
    Tests some basic ops (like +, -, +=)

'''

import sys
import subprocess

from QueryableList import QueryableListObjs, QueryableListDicts, QueryableListMixed

from tutils import filterDictToStr, DataObject, hashableDict


class TestSpecialOps(object):

    def setup_class(self):
        self.dataObjs = [
            DataObject(a='one', b='two', null1=None, emptyStr=''),
            DataObject(a='two', b='five', null1=None, emptyStr=''),
            DataObject(a='three', c='eleven', null1=None, emptyStr=''),
            DataObject(a='four', c='eleven', null1=None, emptyStr=''),
            DataObject(a='five', c='eleven', null1=None, emptyStr=''),
            DataObject(a='six', c='eleven', null1=None, emptyStr=''),
        ]

        self.dataDicts = [ 
            hashableDict({ 'a' : 'one', 'b' : 'two', 'null1' : None, 'emptyStr' : ''}), 
            hashableDict({ 'a' : 'two', 'b' : 'five', 'null1' : None, 'emptyStr' : ''}),
            hashableDict({ 'a' : 'three', 'b' : 'five', 'null1' : None, 'emptyStr' : ''}),
            hashableDict({ 'a' : 'four', 'b' : 'five', 'null1' : None, 'emptyStr' : ''}),
            hashableDict({ 'a' : 'five', 'b' : 'five', 'null1' : None, 'emptyStr' : ''}),
            hashableDict({ 'a' : 'six', 'c' : 'eleven', 'null1' : None, 'emptyStr' : ''}),
        ]

    def _testHasItems(self, results, expectedItems, queryStr=''):
 
        resultsSet = set(results)
        expectedItemsSet = set(expectedItems)

        missingItems = expectedItemsSet - resultsSet

        try:
            assert not missingItems
        except AssertionError as e:
            raise AssertionError('Missing expected item%s: in query { %s }: %s' %(len(missingItems) > 1 and 's' or '', queryStr, str(list(missingItems))) )


        extraItems = resultsSet - expectedItemsSet
        
        try:
            assert not extraItems
        except AssertionError as e:
            raise AssertionError('Got unexpected item%s in query { %s }: %s' %(len(extraItems) > 1 and 's' or '', queryStr, str(list(extraItems))) )

        # Should never be true... but I wanted the verbose results above so I moved this test down
        try:
            assert len(results) == len(expectedItems)
        except AssertionError as e:
            raise AssertionError('Expected query { %s } to return %d objects. Got: %d' %(queryStr, len(expectedObjs), len(results)) )



    def test_add(self):

        testHasItems = self._testHasItems

        qObjs1 = QueryableListObjs([self.dataObjs[0], self.dataObjs[1]])
        qObjs2 = QueryableListObjs([self.dataObjs[3], self.dataObjs[5]])


        addRes = qObjs1 + qObjs2

        # Assert add appends 2 to 1
        testHasItems(addRes, [self.dataObjs[0], self.dataObjs[1], self.dataObjs[3], self.dataObjs[5]], 'o1[0,1] + o2[3,5] = o3[0,1,3,5]')

        # Assert originals are unchanged
        testHasItems(qObjs1, [self.dataObjs[0], self.dataObjs[1]], 'o1 = [0,1]')
        testHasItems(qObjs2, [self.dataObjs[3], self.dataObjs[5]], 'o2 = [3,5]')

        qDicts1 = QueryableListDicts([self.dataDicts[0], self.dataDicts[1]])
        qDicts2 = QueryableListDicts([self.dataDicts[3], self.dataDicts[5]])


        addRes = qDicts1 + qDicts2

        # Assert add appends 2 to 1
        testHasItems(addRes, [self.dataDicts[0], self.dataDicts[1], self.dataDicts[3], self.dataDicts[5]], 'd1[0,1] + d2[3,5] = d3[0,1,3,5]')

        # Assert originals are unchanged
        testHasItems(qDicts1, [self.dataDicts[0], self.dataDicts[1]], 'd1 = [0,1]')
        testHasItems(qDicts2, [self.dataDicts[3], self.dataDicts[5]], 'd1 = [3,5]')

    def test_iadd(self):
        testHasItems = self._testHasItems


        qObjs1 = QueryableListObjs([self.dataObjs[0], self.dataObjs[1]])
        qObjs2 = QueryableListObjs([self.dataObjs[3], self.dataObjs[5]])

        origRef1 = qObjs1

        origID1 = id(qObjs1)

        qObjs1 += qObjs2

        # Assert add appends 2 to 1
        testHasItems(qObjs1, [self.dataObjs[0], self.dataObjs[1], self.dataObjs[3], self.dataObjs[5]], 'o1[0,1] += o2[3,5] = o1[0,1,3,5]')

        # Assert original1 is modified, 2 is not
        testHasItems(origRef1, [self.dataObjs[0], self.dataObjs[1], self.dataObjs[3], self.dataObjs[5]], 'o1 = [0,1,3,5]')
        testHasItems(qObjs2, [self.dataObjs[3], self.dataObjs[5]], 'o2 = [3,5]')

        afterID1 = id(qObjs1)

        assert origID1 == afterID1 , 'Expected id to not change after iadd (i.e. a copy was not made.)\nBefore = %d\nAfter  = %d' %(origID1, afterID1)

        qDicts1 = QueryableListDicts([self.dataDicts[0], self.dataDicts[1]])
        qDicts2 = QueryableListDicts([self.dataDicts[3], self.dataDicts[5]])

        origRef1 = qDicts1

        origID1 = id(qDicts1)

        qDicts1 += qDicts2

        # Assert add appends 2 to 1
        testHasItems(qDicts1, [self.dataDicts[0], self.dataDicts[1], self.dataDicts[3], self.dataDicts[5]], 'd1[0,1] += d2[3,5] = d1[0,1,3,5]')

        # Assert original1 is modified, 2 is not
        testHasItems(origRef1, [self.dataDicts[0], self.dataDicts[1], self.dataDicts[3], self.dataDicts[5]], 'd1 = [0,1,3,5]')
        testHasItems(qDicts2, [self.dataDicts[3], self.dataDicts[5]], 'd2 = [3,5]')

        afterID1 = id(qDicts1)

        assert origID1 == afterID1 , 'Expected id to not change after iadd (i.e. a copy was not made.)\nBefore = %d\nAfter  = %d' %(origID1, afterID1)


#    def test_

if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait())
