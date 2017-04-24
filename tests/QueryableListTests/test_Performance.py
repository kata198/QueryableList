#!/usr/bin/env GoodTests.py

# vim: set ts=4 st=4 sw=4 expandtab :
''' 
   test_Perforamnce.py - A simple test for roughly measuring performance.
     It's not good, or else caching key fetches really has no impact.

'''

import os
import time
import random
import sys
import subprocess

from QueryableList import QueryableListObjs, QueryableListDicts, QueryableListMixed

from tutils import DataObject

NUM = int(os.environ.get('NUM', 1000))

NUMI = int(os.environ.get('NUMI', 1000))

class TestPerformance(object):


    @staticmethod
    def getData(num):
        dataObjs = []
        dataDicts = []

        for i in range(num):
            a = 'x' * random.randint(1, 5)
            b = 'y' * random.randint(1, 5)
            num = random.randint(1, 500)

            dataObjs.append(DataObject(a=a, b=b, num=num) )
            dataDicts.append({'a' : a, 'b' : b, 'num' : num})

        return (dataObjs, dataDicts)

    def setup_class(self):

        data = TestPerformance.getData(NUM)

        (self.dataObjs, self.dataDicts) = data


    def test_performance(self):
        # Test __eq and = both
        qlObjs = QueryableListObjs(self.dataObjs)
        qlDicts = QueryableListDicts(self.dataDicts)


        start = time.time()

        for i in range(1, NUMI+1, 1):
            filterA = 'x' * ((i * 7) % 5)
            filterA2 = 'x' * ((i * 13) % 5)

            filterB = 'y' * ((i*11) % 5)
            filterB2 = 'y' * ((i * 3) % 5)

            filterNums1 = [ (i * 100) % 5, (i * 33) % 5, (i * 121) % 5 ]
            filterNums2 = [ (i * 177) % 5, (i * 62) % 5, (i * 101) % 5 ]

            res = qlObjs.filter(a=filterA, a__ne=filterB, b__in=[filterB[:min(len(filterB)-1, 1)], filterB]).filterOr( num__gt=filterNums1[i % 3], num__ne=filterNums2[i % 3])

        end = time.time()

        print ( "Total time: %f" %(end - start, ))



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())

# vim: set ts=4 st=4 sw=4 expandtab :
