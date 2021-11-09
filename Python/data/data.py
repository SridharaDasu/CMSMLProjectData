import os
import pandas
from Python.util.data_reader import *

def data_gen(n=1000, REGION_TYPE='BACKGROUND'):
    data_gen = DataStream()
    print('%s data generation in process' % REGION_TYPE)
    data_gen.generate_data(n, REGION_TYPE)


# Simple Raw Data data  Generator
if __name__=='__main__':
    data_gen()
