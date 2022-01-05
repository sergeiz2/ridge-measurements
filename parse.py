#!/usr/bin/env python

import pandas as pd
import numpy as np
import mysql.connector as mysql
import os
import re
from pandas.core.frame import DataFrame
from pandas.core.indexes.base import Index
from pandas.core.reshape.merge import merge

from pandas.core.series import Series

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

def find_where_radial(first_col):

    global r_loc_list

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

    r_loc_list = [
        ("r1", r1_ind),
        ("r2", r2_ind),
        ("r3", r3_ind)
    ]
    
    # print(r_loc_list)

    return r_loc_list


def find_where_cht(first_col):
    '''Find where center, head, tip'''
    
    global cht_loc_list
    
    ctr_loc_vals = []
    head_loc_vals = []
    tip_loc_vals = []
    ctr_loc_keys = []
    head_loc_keys = []
    tip_loc_keys = []

    for i in range(len(first_col)):
        if bool(re.search(r'(center)|(middle)', first_col[i])):
            ctr_loc_vals.append(i)

        if bool(re.search(r'(head)', first_col[i])):
            head_loc_vals.append(i)
        
        if bool(re.search(r'(tip)', first_col[i])):
            tip_loc_vals.append(i)

    
    for val in ctr_loc_vals: ctr_loc_keys.append('center')
    for val in head_loc_vals: head_loc_keys.append('head')
    for val in tip_loc_vals: tip_loc_keys.append('tip')
    
    head_loc_keys.extend(tip_loc_keys)
    head_loc_vals.extend(tip_loc_vals)
    ctr_loc_keys.extend(head_loc_keys)
    ctr_loc_vals.extend(head_loc_vals)

    cht_loc_list = list(zip(ctr_loc_keys, ctr_loc_vals))
    
    # print(cht_loc_list)

    return cht_loc_list

    # 'R3'.casefold() in (str(val).casefold() for val in first_col))

def find_where_tf(first_col):
    '''find where thread, flat'''
    
    global tf_loc_list

    thread_loc_vals = []
    thread_loc_keys = []
    flat_loc_vals = []
    flat_loc_keys = [] 

    for i in range(len(first_col)):
        if bool(re.search(r'(thread)|(high)', first_col[i])):
            thread_loc_vals.append(i)
            # print("added thread")
        if bool(re.search(r'(flat)|(low)', first_col[i])):
            flat_loc_vals.append(i)
            # print("added flat")

    # print("threads at: " + str(thread_loc_vals))
    # print("flats at: " + str(flat_loc_vals))

    for val in thread_loc_vals: thread_loc_keys.append('thread')
    # print(thread_loc_keys)
    for val in flat_loc_vals: flat_loc_keys.append('flat')
    # print(flat_loc_keys)

    thread_loc_keys.extend(flat_loc_keys)
    thread_loc_vals.extend(flat_loc_vals)

    tf_loc_list = list(zip(thread_loc_keys, thread_loc_vals))
    
    # print(tf_loc_list)
    
    return tf_loc_list

def find_where_img_suffixes(first_col):
    
    cleaned = [(val, idx) for idx, val in enumerate(first_col, 0) if not bool(re.search(r'(^\d+$)|(\b[^\d\W]+\b)', val))]

    # print(cleaned)

    return cleaned


def sort_locs(first_col):

    merged = []
    merged.extend(find_where_radial(first_col))
    merged.extend(find_where_cht(first_col))
    merged.extend(find_where_tf(first_col))
    merged.extend(find_where_img_suffixes(first_col))

    idx, vals = zip(*merged)
    # print(vals)

    merged_series = pd.Series(vals, idx, name="LocationSeries")
    
    sorted = merged_series.sort_values(ascending=True)
    
    # print(sorted)
    
    return sorted

def find_sample_name(pathstr=None):

    try: 
        sample_name = re.search('DIS_([A-Z][0-9][0-9])_([0-9][0-9])', pathstr).group()
        # print('Sample ' + sample_name)
    except AttributeError:
        pass

    return sample_name

def populate_mysql(clean, addl):
    query = "INSERT INTO index_tracker (sample_id, fluence, dims, batch, image, radial_loc, linear_loc, thread_loc, line_count, line_len, line_ints, wavelength) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    
    values = (name, *radial_locs)

    # print(values)

    cursor.execute(query, values)
    db.commit()

def locate(line_idx, loc_data):
    '''locates a line and determines which image it belongs to'''
    
    loc_img_dict = {
        'image_name': None,
        'radial_loc': None,
        'linear_loc': None,
        'thread_loc': None
    }

    for i in range(line_idx, -1, -1):

        loc_name = loc_data[loc_data == i].index.values.tolist()
        
        # print('loc_name list: ' + str(loc_name))

        for loc in loc_name:

            if re.match(r'\b(r[1-3])\b', loc) and loc_img_dict['radial_loc'] == None:
                loc_img_dict['radial_loc'] = loc
                # print("radial set")

            elif re.match(r'(\b(head)\b)|(\b(center)\b)|(\b(tip)\b)', loc) and loc_img_dict['linear_loc'] == None:
                loc_img_dict['linear_loc'] = loc
                # print("linear set")

            elif re.match(r'(\b(thread)\b)|(\b(flat)\b)', loc) and loc_img_dict['thread_loc'] == None:
                loc_img_dict['thread_loc'] = loc
                # print("thread set")
            
            elif re.match(r'^(?!\s*$).+', loc) and loc_img_dict['image_name'] == None:
                loc_img_dict['image_name'] = loc
                # print("name set to " + loc)

            if loc_img_dict['linear_loc'] == None and loc_img_dict['thread_loc'] != None and loc_img_dict['radial_loc'] != None:
                loc_img_dict['linear_loc'] = 'center'
                # print("linear set to center")
        
    # print('loc_img_dict: ' + str(loc_img_dict))

    return loc_img_dict


def reformat_data(df, loc_data, samp_name):
    
    df.drop(df.columns[list(range(1,6)) + [8]], axis=1, inplace=True)
    df = df.fillna('')

    regex = r'^[1-9]\d*$'
    mask = df[df.columns[0]].str.contains(regex)
    df = df[mask].rename(columns={df.columns[0]: 'line_count', df.columns[1]: 'l', df.columns[2]: 'r'})
    
    df['l/r'] = df.apply(lambda div: float(div.l) / float(div.r), axis=1)

    df['sample_name'] = samp_name

    dict_col = []
    for idx in df.index.tolist():
        dict_col.append(locate(idx, loc_data))
    
    line_idxs = df.index.tolist()
    # print(line_idxs)

    loc_df = pd.DataFrame({'locs': dict_col})
    loc_df = pd.json_normalize(loc_df.locs)
    loc_df['line_idxs'] = line_idxs
    df = df.join(loc_df.set_index('line_idxs'))
    df.reset_index(drop=True, inplace=True)
    print(df)


# def clean_csvs():

#     cursor.execute("DROP TABLE index_tracker")
#     cursor.execute("CREATE TABLE index_tracker (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, sample_id VARCHAR(15), threadcr1_ind SMALLINT, flatcr1_ind SMALLINT, threadhr1_ind SMALLINT, flathr1_ind SMALLINT, threadtr1_ind SMALLINT, flattr1_ind SMALLINT, threadcr2_ind SMALLINT, flatcr2_ind SMALLINT, threadhr2_ind SMALLINT, flathr2_ind SMALLINT, threadtr2_ind SMALLINT, flattr2_ind SMALLINT, threadcr3_ind SMALLINT, flatcr3_ind SMALLINT, threadhr3_ind SMALLINT, flathr3_ind SMALLINT, threadtr3_ind SMALLINT, flattr3_ind SMALLINT)")

#     for file in os.scandir(dir):
#         pth = file.path
#         if 'DIS_A1' in pth:
#             find_sample_name(pth)
            
#             data = pd.read_csv(pth)

#             remove_extra_cols(data)
            
#         first_column = [str(i).lower() for i in data.iloc[:, 0].tolist()]
#         sort_locs(first_column)

#         # populate_index_tracker(sample_name, r_loc_dict.values())

#     # a = cursor.fetchall()

def clean_csvs_test():
    pth = 'C:\\Users\\serge\\OneDrive\\Documents\\ridge-measurements-cleanup\\DIS_T00_00.csv'
    
    sample_name = find_sample_name(pth)
    data = pd.read_csv(pth)

    first_column = [str(i).lower() for i in data.iloc[:, 0].tolist()]
    
    # print(first_column)
    
    location_data = sort_locs(first_column)
    reformat_data(data, location_data, sample_name)
    

# clean_csvs()
clean_csvs_test()

