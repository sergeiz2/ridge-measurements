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

def find_where_radial():

    global r_loc_dict

    try:
        r3_ind = first_col.index('r3')
    except ValueError:
        r3_ind = -1
    
    try:
        r2_ind = first_col.index('r2')
    except ValueError:
        r2_ind = -1
    
    try:
        r1_ind = first_col.index('r1')
    except ValueError:
        r1_ind = 0

    r_loc_dict = {
        "r1_index": r1_ind,
        "r2_index": r2_ind,
        "r3_index": r3_ind
    }

    return r_loc_dict

def find_where_cht():
    '''Find where center, head, tip'''
    
    global center_loc_dict
    global head_loc_dict
    global tip_loc_dict
    
    ctr_loc_vals = []
    head_loc_vals = []
    tip_loc_vals = []
    ctr_loc_keys = ['ctrr1', 'ctrr2', 'ctrr3']
    head_loc_vals = ['headr1', 'headr2', 'headr3']
    tip_loc_vals = ['tipr1', 'tipr2', 'tipr3']

    for i in range(len(first_col)):
        if bool(re.search('*center*|*middle*', first_col[i]):
            ctr_loc_vals.append(i)
        for val in ctr_loc_vals:
            if val < r_loc_dict.get("r2_index"):
                temp = []
                temp.append(val)

        if bool(re.search('*head*', first_col[i]):
            head_loc_vals.append(i)
        
        if bool(re.search('*tip*', first_col[i]):
            tip_loc_vals.append(i)

    

    r_loc_dict = {
        "r1_index": r1_ind,
        "r2_index": r2_ind,
        "r3_index": r3_ind
    }

    return r_loc_dict

    # 'R3'.casefold() in (str(val).casefold() for val in first_col))

def find_sample_name(pathstr=None):
    
    global sample_name

    try: 
        sample_name = re.search('DIS_A([0-9][0-9])_([0-9][0-9])', pathstr).group()
        # print('Sample ' + sample_name)
    except AttributeError:
        pass

    return sample_name

def populate_index_tracker(name, radial_locs):
    query = "INSERT INTO index_tracker (sample_id, threadcr1_ind, flatcr1_ind, threadhr1_ind, flathr1_ind, threadtr1_ind, flattr1_ind, threadcr2_ind, flatcr2_ind, threadhr2_ind, flathr2_ind, threadtr2_ind, flattr2_ind, threadcr3_ind, flatcr3_ind, threadhr3_ind, flathr3_ind, threadtr3_ind, flattr3_ind) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    
    
    values = (name, *radial_locs)

    # print(values)

    cursor.execute(query, values)
    db.commit()


def lines_before(index, df):
    '''checks if there are lines or images "higher up" or "earlier" in the file.'''
    
    first_col = pd.Series(first_col)
    line_locs = first_col[first_col.str.match(r'^[1-9]\d*$')==True]

    print(line_locs)

    # if index 

def clean_csvs():

    global first_col

    cursor.execute("DROP TABLE index_tracker")
    cursor.execute("CREATE TABLE index_tracker (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, sample_id VARCHAR(15), threadcr1_ind SMALLINT, flatcr1_ind SMALLINT, threadhr1_ind SMALLINT, flathr1_ind SMALLINT, threadtr1_ind SMALLINT, flattr1_ind SMALLINT, threadcr2_ind SMALLINT, flatcr2_ind SMALLINT, threadhr2_ind SMALLINT, flathr2_ind SMALLINT, threadtr2_ind SMALLINT, flattr2_ind SMALLINT, threadcr3_ind SMALLINT, flatcr3_ind SMALLINT, threadhr3_ind SMALLINT, flathr3_ind SMALLINT, threadtr3_ind SMALLINT, flattr3_ind SMALLINT)")

    for file in os.scandir(dir):
        pth = file.path
        if 'DIS_A1' in pth:
            find_sample_name(pth)
            
            data = pd.read_csv(pth)
        
            
        first_col = [i.lower for i in data.iloc[:, 0].tolist()]
        find_where_radial()
        # find_where_tch(data)

        populate_index_tracker(sample_name, r_loc_dict.values())

    # a = cursor.fetchall()

    

clean_csvs()
