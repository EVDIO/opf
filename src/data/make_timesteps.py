import os 
import json
import pandas as pd
import numpy as np
import pyreadr



file_names_open = ['cons_nom.json', 'dg_nom.json', 'ess_nom.json', 'ev_nom.json', 'pv_nom.json']
for file in file_names_open:
    path = "C:\\Users\\Dell\\Documents\\GitHub\\opf\\data\\interim\\"+file
    with open(path) as f:
        print(file[:-5])
        globals()[file[:-5]] = json.load(f)

HOURS = 24
DAYS = 1
TIMESTEPS = HOURS*DAYS


mean_active = np.load(r'C:\Users\Dell\Documents\GitHub\opf\data\interim\cons_act_mean.npy')
mean_reactive = np.load(r'C:\Users\Dell\Documents\GitHub\opf\data\interim\cons_react_mean.npy')

mean_active = np.repeat(mean_active[:, np.newaxis], DAYS, axis=1).flatten()
mean_reactive = np.repeat(mean_reactive[:, np.newaxis], DAYS, axis=1).flatten()


num_of_cons = len(cons_nom["Nodes"])

dict_data = {}
for i in range(num_of_cons):

    column_act = 'PD'+'_'+str(i+1)+'_'+str(cons_nom["Nodes"][i])
    column_react = 'QD'+'_'+str(i+1)+'_'+str(cons_nom["Nodes"][i])
    dict_data[column_act] = mean_active
    dict_data[column_react] = mean_reactive


mean_pv = np.load(r'C:\Users\Dell\Documents\GitHub\opf\data\interim\pv_mean.npy')
mean_pv = mean_pv[:TIMESTEPS]


num_of_pv = len(pv_nom["Nodes"])

dict_data = {}
for i in range(num_of_pv):

    column_pv = 'PV'+'_'+str(i+1)+'_'+str(pv_nom["Nodes"][i])
    dict_data[column_pv] = mean_pv


Delta_t = np.ones((TIMESTEPS,))
dict_data['Delta_t'] = Delta_t


result = pyreadr.read_r(path=r'C:\Users\Dell\Documents\GitHub\opf\data\raw\Exercise3.RData')
input_df = result['AllDat']
U = np.array([input_df['Ta'].to_numpy(),input_df['Gv'].to_numpy(),input_df['Ph1'].to_numpy()])

Ti = input_df['Ta'].to_numpy()[:TIMESTEPS]
Gv = input_df['Gv'].to_numpy()[:TIMESTEPS]
Ph = input_df['Ph1'].to_numpy()[:TIMESTEPS]

dict_data['Ti'] = Ti
dict_data['Gv'] = Gv
dict_data['Ph'] = Ph

pt = np.array([0.06243,
0.06015,
0.05723,
0.05266,
0.05497,
0.06119,
0.06153,
0.06481,
0.06973,
0.0802,
0.08381,
0.08643,
0.08449,
0.08613,
0.08778,
0.08943,
0.08716,
0.08717,
0.09862,
0.1,
0.09636,
0.08886,
0.08037,
0.07058
])
np.save(r'C:\Users\Dell\Documents\GitHub\opf\data\interim\pt.npy',pt)
pt = np.repeat(pt[:, np.newaxis], DAYS, axis=1).flatten()

dict_data['pt'] = pt

df_timesteps = pd.DataFrame(dict_data)


df_timesteps.to_csv(r'C:\Users\Dell\Documents\GitHub\opf\data\interim\time_slots.csv')