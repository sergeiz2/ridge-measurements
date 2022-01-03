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

def find_where_radial(df):

    global r_loc_dict 

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

    r_loc_dict = {
        "r1_index": r1_ind,
        "r2_index": r2_ind,
        "r3_index": r3_ind
    }

    return r_loc_dict

    # 'R3'.casefold() in (str(val).casefold() for val in df.iloc[:, 0].tolist()))


def find_sample_name(pathstr=None):
    
    global sample_name

    try: 
        sample_name = re.search('DIS_A([0-9][0-9])_([0-9][0-9])', pathstr).group()
        # print('Sample ' + sample_name)
    except AttributeError:
        pass

    return sample_name

def populate_index_tracker(name, radial_locs):
    query = "INSERT INTO index_tracker (sample_id, r1_ind, r2_ind, r3_ind) VALUES (%s, %s, %s, %s)"
    values = (name, *radial_locs)

    # print(values)

    cursor.execute(query, values)
    db.commit()




def clean_csvs():
    cursor.execute("DROP TABLE index_tracker")
    cursor.execute("CREATE TABLE index_tracker (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, sample_id VARCHAR(15), r1_ind SMALLINT, r2_ind SMALLINT,  r3_ind SMALLINT)")

    for file in os.scandir(dir):
        pth = file.path
        if 'DIS_A1' in pth:
            find_sample_name(pth)
            
            data = pd.read_csv(pth)
        

        find_where_radial(data)

        populate_index_tracker(sample_name, r_loc_dict.values())

    # a = cursor.fetchall()
    
clean_csvs()

