#!/usr/bin/env python

import pandas as pd
import numpy as np
import mysql.connector as mysql
import os
import re

dir = os.getcwd() + '\CSVs'

def find_radial(df):

    try:
        r3_ind = df.iloc[:, 0].tolist().index('R3')
    except ValueError:
        r3_ind = -1
    try:
        r2_ind = df.iloc[:, 0].tolist().index('R2')
    except ValueError:
        r2_ind = -1
    try:
        r1_ind = df.iloc[:, 0].tolist().index('R1')
    except ValueError:
        r1_ind = -1

            

    # 'R3'.casefold() in (str(val).casefold() for val in df.iloc[:, 0].tolist()))


def clean_csv(pathstr=None):
    sample_name = None

    dataframe = pd.read_csv(pathstr)
    
    try: 
        sample_name = re.search('DIS_A([0-9][0-9])_([0-9][0-9])', pathstr).group()
        print('Sample ' + sample_name)
    except AttributeError:
        pass

    find_radial(dataframe)

for file in os.scandir(dir):
    if 'DIS_A1' in file.path:
        clean_csv(file.path)

