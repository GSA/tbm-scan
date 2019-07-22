import csv
import json
import os

def read_json():
    path_to_json = os.path.join(os.getcwd(),'data')
    json_files = [f for f in os.listdir(path_to_json) if f.endswith('.json')]
    all_data = []
    for json_file in json_files:
        json_file = os.path.join(path_to_json, json_file)
        with open(json_file, 'r') as jf:
            data = json.load(jf)
            all_data.append(data)
    
    return all_data


def append_to_csv(json_data):
    '''
    Append data to data.csv after transforming it.
    '''
    #json_data is synoymous with merged_notices_dict as returned by get_nightly_data
    csv_rows, csv_columns = transform_data(json_data)
    csv_file = os.path.join(os.getcwd(), 'data.csv')
    with open(csv_file, 'a+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = csv_columns)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)


def transform_data(json_data):
    '''
    Transofrm the fbo data returned by get_nightly_data so that each notice dictionary contains
    a key stating its notice type. This will make it easier when writing the results to csv.
    '''
    #json_data is synoymous with merged_notices_dict as returned by get_nightly_data
    keys = ['notice type']
    csv_rows = []
    for k in json_data:
        notices = json_data[k]
        for notice in notices:
            csv_row = {}
            csv_row['notice type'] = k
            for key in notice:
                keys.append(key)
                csv_row[key] = notice[key]
            csv_rows.append(csv_row)
    csv_columns = set(keys)

    return csv_rows, csv_columns

def write_to_csv():
    all_data = read_json()
    [append_to_csv(x) for x in all_data]
