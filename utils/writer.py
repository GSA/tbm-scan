import csv
from datetime import datetime
import json
import os
import sys

import pandas as pd

def read_json():
    path_to_json = os.path.join(os.getcwd(),'data')
    json_files = [f for f in os.listdir(path_to_json) if f.endswith('.json')]
    if not json_files:
        print("\tThere's no new FBO data. Wait another day to run this scan.")
        print("\tThis means you can safefully ignore the following error message.")
        print("*"*80)
        sys.exit(0)
    files_to_delete = []
    all_data = []
    for json_file in json_files:
        json_file = os.path.join(path_to_json, json_file)
        files_to_delete.append(json_file)
        with open(json_file, 'r') as jf:
            data = json.load(jf)
            fbo_date = "".join(s for s in json_file if s.isdigit())
            all_data.append((fbo_date, data))
    
    return all_data, files_to_delete


def data_to_df(json_data, field_filter = False):
    '''
    Append data to data.csv after transforming it.
    '''
    csv_rows = transform_data(json_data, field_filter)
    df = pd.DataFrame(csv_rows)
    
    return df
    

def transform_data(json_data, field_filter = False):
    '''
    Transform the fbo data returned by get_nightly_data so that each notice dictionary contains
    a key stating its notice type. This will make it easier when writing the results to csv.
    '''
    user_desired_fields = {'AGENCY','CONTACT','DATE','DESC','LOCATION',
                           'NAICS','RESPDATE','SETASIDE',
                           'SOLNBR','SUBJECT','URL','YEAR'}
    csv_rows = []
    fbo_date, data = json_data
    all_empty = True
    for k in data:
        notices = data[k]
        for notice in notices:
            csv_row = {}
            csv_row['notice type'] = k
            csv_row['fbo date'] = fbo_date
            for key in notice:
                if field_filter:
                    if key in user_desired_fields:
                        csv_row[key] = notice[key]
                else:
                    csv_row[key] = notice[key]
            csv_rows.append(csv_row)
            all_empty = False
    if all_empty:
        #Be sure we insert an empty row with the fbo date to prevent duplicative future scans
        csv_rows.append({'fbo date': fbo_date,'notice type': 'NA'})

    return csv_rows

def get_last_scan_date(csv_file):
    df = pd.read_csv(csv_file, dtype = str)
    dates = df['fbo date'].astype(str)
    last_scan_date = dates.apply(lambda x: datetime.strptime(x, "%Y%m%d")).max()

    return last_scan_date


def write_to_csv(field_filter = False):
    all_data, files_to_delete = read_json()
    dfs = [data_to_df(x, field_filter) for x in all_data]
    df = pd.concat(dfs, ignore_index=True, sort=True)
    csv_file = os.path.join(os.getcwd(), 'data.csv')
    csv_exists = os.path.exists(csv_file)
    if csv_exists:
        #if there's a pre-existing csv, read it in to concat with this one
        pre_existing_df = pd.read_csv(csv_file, dtype = str)
        updated_df = pd.concat([df, pre_existing_df], ignore_index=True, sort=True)
        updated_df.to_csv(csv_file, index = False)
    else:
        #if there's no pre-existing csv, write what we've got as the first one
        df.to_csv(csv_file, index = False)
    #clean up the json files
    [os.remove(f) for f in files_to_delete]
