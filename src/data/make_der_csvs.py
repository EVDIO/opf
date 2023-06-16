import os
import pandas as pd
import numpy as np
import json


def append_data(name, row_val,row, dict_):
    if row_val == name:
        # append new values to each list in the dictionary
        for j, (key, value) in enumerate(dict_.items()):
            if dict_["Nodes"]:
                if key == "Nodes":
                    dict_[key].append(row[0])
                else:
                    dict_[key].append(value[0])
            else:
                dict_["Nodes"].append(row[0])
                break

def process_files(input_path_nodes,output_path):
    df_nodes = pd.read_csv(input_path_nodes)

    columns_list = ['Nodes']
    ENERGY_RESOURCE = 'energy_resource'
    NUMBER = 5
    for i in range(1, NUMBER + 1):
        columns_list.append(ENERGY_RESOURCE + str(i))

    df_resources = df_nodes[columns_list]

    file_names_open = ['cons_nom.json', 'dg_nom.json', 'ess_nom.json', 'ev_nom.json', 'pv_nom.json']
    for file in file_names_open:
        file_path = os.path.join(os.getcwd(), 'data', 'interim', file)
        with open(file_path) as f:
            print(file[:-5])
            globals()[file[:-5]] = json.load(f)

    for index, row in df_resources.iterrows():
        for i, row_val in enumerate(row):
            append_data('cons', row_val ,row, cons_nom)
            append_data('dg',row_val ,row, dg_nom)
            append_data('ev', row_val, row, ev_nom)
            append_data('ess', row_val, row, ess_nom)
            append_data('pv', row_val, row, pv_nom)

    for file in file_names_open:
        output_filename = 'df_' + file[:-9] + '.csv'
        output_path_save = os.path.join(output_path,output_filename)
        print('df_' + file[:-9])
        globals()['df_' + file[:-9]] = pd.DataFrame(globals()[file[:-5]])
        globals()['df_' + file[:-9]].to_csv(output_path_save)

    print('DER data saved!')

if __name__ == "__main__":
    # Get the root directory path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(root_dir, '..')

    # Construct input and output paths using relative paths
    input_path_nodes = os.path.join(raw_data_dir, 'data', 'processed', 'nodes_33.csv')
    output_path = os.path.join(raw_data_dir, 'data', 'processed')
 
    process_files(input_path_nodes,output_path)