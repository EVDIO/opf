import os 
import pandas as pd
import numpy as np
import pyreadr


def create_timestep_data(HOURS,DAYS,interim_path,processed_path):

    TIMESTEPS = HOURS*DAYS
    file_names_open = ['asset_cons.csv', 'asset_dg.csv',
                       'asset_ess.csv', 'asset_pv.csv',
                       'asset_ev.csv']

    for file in file_names_open:
        path = os.path.join(processed_path, file)
        with open(path) as f:
            print(file[:-4])
            globals()[file[:-4]] = pd.read_csv(f)

    # Create timestep data for consumers 
    mean_active = np.load(os.path.join(interim_path, 'cons_act_mean.npy'))
    mean_reactive = np.load(os.path.join(interim_path, 'cons_react_mean.npy'))

    mean_active = np.repeat(mean_active[:, np.newaxis], DAYS, axis=1).flatten()
    mean_reactive = np.repeat(mean_reactive[:, np.newaxis], DAYS, axis=1).flatten()

    num_of_cons = len(asset_cons["Nodes"])

    dict_data = {}
    for i in range(num_of_cons):

        column_act = 'PD'+'_'+str(asset_cons["Nodes"][i])+'_'+str(i)
        column_react = 'QD'+'_'+str(asset_cons["Nodes"][i])+'_'+str(i)
        dict_data[column_act] = mean_active
        dict_data[column_react] = mean_reactive

    # Create timestep data for pv
    mean_pv = np.load(os.path.join(interim_path,'pv_mean.npy'))
    mean_pv = mean_pv[:TIMESTEPS]

    num_of_pv = len(asset_pv["Nodes"])

    for i in range(num_of_pv):

        column_pv = 'PV'+'_'+str(asset_pv["Nodes"][i])+'_'+str(i)
        dict_data[column_pv] = mean_pv


    # Create delta t
    Delta_t = np.ones((TIMESTEPS,))
    dict_data['Delta_t'] = Delta_t

    # Create timestep data for the thermal model.
    result = pyreadr.read_r(path=os.path.join(interim_path,'Exercise3.RData'))
    input_df = result['AllDat']
    U = np.array([input_df['Ta'].to_numpy(),input_df['Gv'].to_numpy(),input_df['Ph1'].to_numpy()])

    Ti = input_df['Ta'].to_numpy()[:TIMESTEPS]
    Gv = input_df['Gv'].to_numpy()[:TIMESTEPS]
    Ph = input_df['Ph1'].to_numpy()[:TIMESTEPS]

    dict_data['Ti'] = Ti
    dict_data['Gv'] = Gv
    dict_data['Ph'] = Ph

    # Price of power
    pt = np.load(os.path.join(interim_path,'pt.npy'))
    pt = np.repeat(pt[:, np.newaxis], DAYS, axis=1).flatten()

    dict_data['pt'] = pt

    df_timesteps = pd.DataFrame(dict_data)

    df_timesteps.to_csv(os.path.join(processed_path,'time_slots.csv'))


if __name__ == '__main__':

    HOURS = 24
    DAYS = 1    

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, '..')

    # Construct input and output paths using relative paths
    interim_path = os.path.join(data_dir, 'data', 'interim')
    processed_path = os.path.join(data_dir, 'data', 'processed')

    create_timestep_data(HOURS,DAYS,interim_path,processed_path)