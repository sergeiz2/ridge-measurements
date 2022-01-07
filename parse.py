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
import warnings

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

def _small_warning(msg, *args, **kwargs):
    return str(msg) + '\n'
warnings.formatwarning = _small_warning

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
        if bool(re.search(r'(center)|(middle)|(mid)', first_col[i])):
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

def populate_mysql(cleaned, addl, samp_name):
    query = "INSERT INTO pedicle_screw_summary (sample_id, fluence, dims, batch, image, radial_loc, linear_loc, thread_loc, line_count, line_len, line_ints, wavelength) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    addl.drop([*range(0,11)], inplace=True)
    addl.drop(addl.columns[list(range(4, len(addl.columns)))], axis=1, inplace=True)
    
    # print(addl)

    flu = addl.loc[addl[addl.columns[2]] == samp_name, addl.columns[0]].iloc[0]
    dims = addl.loc[addl[addl.columns[2]] == samp_name, addl.columns[1]].iloc[1]
    bat = addl.loc[addl[addl.columns[2]] == samp_name, addl.columns[3]].iloc[3]
    imgs = cleaned['image_name'].tolist()
    rad_locs = cleaned['radial_loc'].tolist()
    lin_locs = cleaned['linear_loc'].tolist()
    thr_locs = cleaned['thread_loc'].tolist()
    ln_cnt = cleaned['line_count'].tolist()
    l = cleaned['l'].tolist()
    r = cleaned['r'].tolist()
    wavelen = cleaned['l_over_r'].tolist()

    values = [*zip(((samp_name, flu, dims, bat) for i in imgs), imgs, rad_locs, lin_locs, thr_locs, ln_cnt, l, r, wavelen)]
    values = [(*x, i, ra, li, t, ln, l, r, w) for x, i, ra, li, t, ln, l, r, w in values]
    # values = [np.nan_to_num(v, nan=-1) for v in values]

    # print(values)

    cursor.executemany(query, values)

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

def drop_bad_data(df):
        
        # df = df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        # TODO: does this replace row if less than 3 non-na? That's what we need. 
        df.dropna(axis=1, how='all', thresh=2, inplace=True)
        df.dropna(axis=0, how='all', thresh=1, inplace=True)

        drop_df = pd.DataFrame()
        # TODO: CHECK IF DF PASSED by reference!!
        col_count = len(df.columns)


        def check_if_contains_numbers(ser):
            thresh = 2
            for i in ser.array:
                ctr = 1
                try:
                    if re.match(r'^\d*?(([.,]\d)|(\d[.,])\d*?)?$', i):
                        ctr += 1
                        if ctr >= thresh:
                            return ser
                except TypeError:
                    pass

            return pd.Series()
        
        df.drop(df.columns[list(range(1,6)) + [8]], axis=1, inplace=True)
        addl_drop = df.iloc[:, 3:col_count+1]
        for _, s in addl_drop.iteritems():
            drop_df = pd.concat([drop_df, check_if_contains_numbers(s)], axis=1, copy=False)

        df.drop(addl_drop.columns, axis=1, inplace=True)

        return drop_df

def clean_text(df):
    regex = r'^[1-9]\d*$'
    mask = df[df.columns[0]].str.contains(regex).fillna(False)
    return df[mask]

def check_fix_small_val(df, row_id, samp_name, img_name, col_name='l'):
    val = df.loc[row_id, col_name]
    if val < 10.0: 
        warnings.warn("Small value (" + str(val) + ") detected in sample " + 
            str(samp_name) + ", image " + str(img_name) + 
            ". Assuming micrometers and multiplying by 1000...", UserWarning)
            
        df.at[row_id, 'l'] = val*1000

def reformat_data(df, loc_data, samp_name):

    bad_data = drop_bad_data(df)
    if bad_data.empty:
        pass
    else:
        warnings.warn("Discarding the following data from sample " + str(samp_name) + 
            "! Reformat CSVs appropriately if you'd like to include this data. \n\n" + 
            bad_data.to_string())
    
    df = clean_text(df)
    df.rename(columns={df.columns[0]: 'line_count', df.columns[1]: 'l', df.columns[2]: 'r'}, inplace=True)
    
    # FIXME: fix the warning generated below. Read about views vs copies of df.
    df = df.astype(float, copy=False)
    
    df['sample_name'] = samp_name

    dict_col = []
    for idx in df.index.tolist():
        loc_dict = locate(idx, loc_data)

        check_fix_small_val(df, idx, samp_name, img_name=loc_dict.get('image_name'), col_name='l')

        dict_col.append(loc_dict)

    df['l_over_r'] = df['l']/df['r']
    
    line_idxs = df.index.tolist()
    # print(line_idxs)

    loc_df = pd.DataFrame({'locs': dict_col})
    loc_df = pd.json_normalize(loc_df.locs)
    loc_df['line_idxs'] = line_idxs

    df = df.join(loc_df.set_index('line_idxs'))
    df.reset_index(drop=True, inplace=True)
    
    # print(df)
    print(samp_name)

    return df

def clean_csvs():

    cursor.execute("DROP TABLE pedicle_screw_summary")
    cursor.execute("CREATE TABLE pedicle_screw_summary (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, sample_id VARCHAR(15), fluence FLOAT(24), dims VARCHAR(15), batch VARCHAR(15), image VARCHAR(50), radial_loc VARCHAR(3), linear_loc VARCHAR(7), thread_loc VARCHAR(7), line_count SMALLINT, line_len FLOAT, line_ints SMALLINT, wavelength FLOAT(10))")

    for file in os.scandir(dir):
        pth = file.path
        #TODO: Add try-catch
        summary = pd.read_csv('C:\\Users\\serge\\OneDrive\\Documents\\ridge-measurements-cleanup\\CSVs\\Ridge Measurements_Summary.csv')

        if 'DIS_A1' in pth:
            sample_name = find_sample_name(pth)
            
            data = pd.read_csv(pth)
            
            first_column = [str(i).lower() for i in data.iloc[:, 0].tolist()]
            location_data = sort_locs(first_column)
            
            populate_mysql(reformat_data(data, location_data, sample_name), summary, sample_name)

    # a = cursor.fetchall()

def clean_csvs_test():
    pth = 'C:\\Users\\serge\\OneDrive\\Documents\\ridge-measurements-cleanup\\DIS_T00_00.csv'
    
    sample_name = find_sample_name(pth)
    data = pd.read_csv(pth)

    first_column = [str(i).lower() for i in data.iloc[:, 0].tolist()]
    
    # print(first_column)
    
    location_data = sort_locs(first_column)
    reformat_data(data, location_data, sample_name)

clean_csvs()
# clean_csvs_test()