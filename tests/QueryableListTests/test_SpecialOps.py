#!/usr/bin/env GoodTests.py

# vim: set ts=4 st=4 sw=4 expandtab :
''' 
    Tests some basic ops (like +, -, +=)

'''

import sys
import subprocess

from QueryableList import QueryableListObjs, QueryableListDicts, QueryableListMixed

from tutils import filterDictToStr, DataObject, hashableDict, assembleItems


gdo = lambda _self, nums : assembleItems(_self.dataObjs, nums)
gdd = lambda _self, nums : assembleItems(_self.dataDicts, nums)

mkNumSet = lambda typeCh, nums : '%s[%s]' %(typeCh, ','.join([str(num) for num in nums]))

def mkOpStr(typeCh, nums1, oper, nums2, nums3=None):
#    lambda _mkNumSet = nums : mkNumSet(typeCh, nums)

    ret = "%s %s" %(mkNumSet(typeCh, nums1), oper)
    if nums3 is not None:
        return ret + " %s = %s" %( mkNumSet(typeCh, nums2), mkNumSet(typeCh, nums3))
    else:
        return ret + " = %s" %(mkNumSet(typeCh, nums2),)

def beforeLastEquals(line):
    try:
        return line[:line.rindex('=')]
    except:
        return line

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
            raise AssertionError('Missing expected item%s: in query { %s }: %s' %(len(missingItems) > 1 and 's' or '', beforeLastEquals(queryStr), str(list(missingItems))) )


        extraItems = resultsSet - expectedItemsSet
        
        try:
            assert not extraItems
        except AssertionError as e:
            raise AssertionError('Got unexpected item%s in query { %s }: %s' %(len(extraItems) > 1 and 's' or '', beforeLastEquals(queryStr), str(list(extraItems))) )

        # Should never be true... but I wanted the verbose results above so I moved this test down
        try:
            assert len(results) == len(expectedItems)
        except AssertionError as e:
            raise AssertionError('Expected query { %s } to return %d objects. Got: %d' %( beforeLastEquals(queryStr), len(expectedItems), len(results)) )




    def test_add(self):

        testHasItems = self._testHasItems

        set1Nums = [0, 1]
        set2Nums = [3, 5]
        set3Nums = [0, 1, 3, 5]

        qObjs1 = QueryableListObjs( gdo(self, set1Nums) )
        qObjs2 = QueryableListObjs( gdo(self, set2Nums) )


        addRes = qObjs1 + qObjs2

        # Assert add appends 2 to 1
        testHasItems(addRes, gdo(self, set3Nums), mkOpStr('o', set1Nums, '+', set2Nums, set3Nums) )

        # Assert originals are unchanged
        testHasItems(qObjs1, gdo(self, set1Nums) )
        testHasItems(qObjs2, gdo(self, set2Nums) )

        qDicts1 = QueryableListDicts( gdd(self, set1Nums) )
        qDicts2 = QueryableListDicts( gdd(self, set2Nums) )


        addRes = qDicts1 + qDicts2

        # Assert add appends 2 to 1
        testHasItems(addRes, gdd(self, set3Nums), mkOpStr('d', set1Nums, '+', set2Nums, set3Nums) )

        # Assert originals are unchanged
        testHasItems(qDicts1, gdd(self, set1Nums), mkNumSet('d', set1Nums) )
        testHasItems(qDicts2, gdd(self, set2Nums), mkNumSet('d', set2Nums) )

    def test_iadd(self):
        testHasItems = self._testHasItems

        set1Nums = [0, 1]
        set2Nums = [3, 5]
        set3Nums = [0, 1, 3, 5]

        qObjs1 = QueryableListObjs( gdo(self, set1Nums) )
        qObjs2 = QueryableListObjs( gdo(self, set2Nums) )

        origRef1 = qObjs1

        origID1 = id(qObjs1)

        qObjs1 += qObjs2

        # Assert add appends 2 to 1
        testHasItems(qObjs1, gdo(self, set3Nums), mkOpStr('o', set1Nums, '+=', set2Nums) )

        # Assert original1 is modified, 2 is not
        testHasItems(qObjs1,  gdo(self, set3Nums), mkNumSet('o', set3Nums) )
        testHasItems(qObjs2,  gdo(self, set2Nums), mkNumSet('o', set2Nums) )

        afterID1 = id(qObjs1)

        assert origID1 == afterID1 , 'Expected id to not change after iadd (i.e. a copy was not made.)\nBefore = %d\nAfter  = %d' %(origID1, afterID1)

        testHasItems(origRef1,  gdo(self, set3Nums), mkNumSet('o', set3Nums) )

        qDicts1 = QueryableListDicts( gdd(self, set1Nums) )
        qDicts2 = QueryableListDicts( gdd(self, set2Nums) )

        origRef1 = qDicts1

        origID1 = id(qDicts1)

        qDicts1 += qDicts2

        # Assert add appends 2 to 1
        testHasItems(qDicts1, gdd(self, set3Nums), mkOpStr('d', set1Nums, '+', set2Nums, set3Nums) )

        # Assert original1 is modified, 2 is not
        testHasItems(qDicts1,  gdd(self, set3Nums), mkNumSet('d', set3Nums) )
        testHasItems(qDicts2,  gdd(self, set2Nums), mkNumSet('d', set2Nums) )

        afterID1 = id(qDicts1)

        assert origID1 == afterID1 , 'Expected id to not change after iadd (i.e. a copy was not made.)\nBefore = %d\nAfter  = %d' %(origID1, afterID1)
        testHasItems(origRef1,  gdd(self, set3Nums), mkNumSet('d', set3Nums) )

    def test_sub(self):

        testHasItems = self._testHasItems

        set1Nums = [0, 1, 5, 1, 3]
        set2Nums = [3, 1]
        set3Nums = [0, 5]

        qObjs1 = QueryableListObjs( gdo(self, set1Nums) )
        qObjs2 = QueryableListObjs( gdo(self, set2Nums) )


        subRes = qObjs1 - qObjs2

        # Assert sub removes items in 2 from 1
        testHasItems(subRes, gdo(self, set3Nums), mkOpStr('o', set1Nums, '-', set2Nums, set3Nums) )

        # Assert originals are unchanged
        testHasItems(qObjs1, gdo(self, set1Nums), mkNumSet('o', set1Nums) )
        testHasItems(qObjs2, gdo(self, set2Nums), mkNumSet('o', set2Nums) )

        qDicts1 = QueryableListDicts( gdd(self, set1Nums) )
        qDicts2 = QueryableListDicts( gdd(self, set2Nums) )


        subRes = qDicts1 - qDicts2

        # Assert sub removes items in 2 from 1
        testHasItems(subRes, gdd(self, set3Nums), mkOpStr('d', set1Nums, '-', set2Nums, set3Nums) )

        # Assert originals are unchanged
        testHasItems(qDicts1, gdd(self, set1Nums), mkNumSet('d', set1Nums) )
        testHasItems(qDicts2, gdd(self, set2Nums), mkNumSet('d', set2Nums) )

    def test_isub(self):
        testHasItems = self._testHasItems


        set1Nums = [0, 1, 5, 1, 3] # A
        set2Nums = [3, 1]          # B

        set3Nums = [0, 5]          # = C

        qObjs1 = QueryableListObjs( gdo(self, [0, 1, 5, 1, 3]) )
        qObjs2 = QueryableListObjs( gdo(self, [3, 1]) )

        origRef1 = qObjs1

        origID1 = id(qObjs1)

        qObjs1 -= qObjs2

        # Assert sub removes items from 1 that are in 2
        testHasItems(qObjs1, gdo(self, set3Nums), mkOpStr('o', set1Nums, '-', set2Nums, set3Nums)) 

        # Assert original1 is modified, 2 is not
        testHasItems(qObjs1, gdo(self, set3Nums), 'o1 = ' + mkNumSet('o', set3Nums))
        testHasItems(qObjs2, gdo(self, set2Nums), 'o2 = ' + mkNumSet('o', set2Nums))

        afterID1 = id(qObjs1)

        assert origID1 == afterID1 , 'Expected id to not change after iadd (i.e. a copy was not made.)\nBefore = %d\nAfter  = %d' %(origID1, afterID1)
        testHasItems(origRef1, gdo(self, set3Nums), 'o1ref = ' + mkNumSet('o', set3Nums))

        qDicts1 = QueryableListDicts( gdd(self, set1Nums) )
        qDicts2 = QueryableListDicts( gdd(self, set2Nums) )

        origRef1 = qDicts1

        origID1 = id(qDicts1)

        qDicts1 -= qDicts2

        # Assert sub removes items from 1 that are in 2
        testHasItems(qDicts1, gdd(self, set3Nums), mkOpStr('d', set1Nums, '-=', set2Nums))

        # Assert original1 is modified, 2 is not
        testHasItems(qDicts1, gdd(self, set3Nums), 'd1 = ' + mkNumSet('d', set3Nums) )
        testHasItems(qDicts2, gdd(self, set2Nums), 'd1 = ' + mkNumSet('d', set2Nums) )

        afterID1 = id(qDicts1)

        assert origID1 == afterID1 , 'Expected id to not change after iadd (i.e. a copy was not made.)\nBefore = %d\nAfter  = %d' %(origID1, afterID1)
        testHasItems(origRef1, gdd(self, set3Nums), 'd1ref = ' + mkNumSet('d', set3Nums) )


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())


# vim: set ts=4 st=4 sw=4 expandtab :
