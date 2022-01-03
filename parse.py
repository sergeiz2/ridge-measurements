#!/usr/bin/env python

import pandas as pd
import numpy as np
import mysql.connector as mysql
import os
import re

dir = os.getcwd() + '\CSVs'

db = mysql.connect(
    host = "localhost",
    user = "editekk",
    passwd = "editekk",
    database = "RidgeMeasurements"
)
cursor = db.cursor()

# print(db)
# cursor.execute("SHOW DATABASES")
# print(cursor.fetchall())

def find_radial(df):

    global r3_ind
    global r2_ind
    global r1_ind

    try:
        r3_ind = df.iloc[:, 0].tolist().index('R3')
    
    except ValueError:
        try:
            r3_ind = df.iloc[:, 0].tolist().index('r3')
        except ValueError:
            r3_ind = -1
    
    try:
        r2_ind = df.iloc[:, 0].tolist().index('R2')
    
    except ValueError:
        try:
            r2_ind = df.iloc[:, 0].tolist().index('r2')
        except ValueError:
            r2_ind = -1
    
    try:
        r1_ind = df.iloc[:, 0].tolist().index('R1')
    
    except ValueError:
        try:
            r1_ind = df.iloc[:, 0].tolist().index('r1')
        except ValueError:
            r1_ind = -1

            

    # 'R3'.casefold() in (str(val).casefold() for val in df.iloc[:, 0].tolist()))


def find_sample_names(pathstr=None):
    sample_name = None

    dataframe = pd.read_csv(pathstr)
    
    try: 
        sample_name = re.search('DIS_A([0-9][0-9])_([0-9][0-9])', pathstr).group()
        # print('Sample ' + sample_name)
    except AttributeError:
        pass

    find_radial(dataframe)

def clean_csv():
    for file in os.scandir(dir):
        if 'DIS_A1' in file.path:
            find_sample_names(file.path)

