# Import libraries
import pandas as pd
import numpy as np
import pyreadr

def get_data_time(path_time):

    """
    Read time data from csv file and return relevant information as dictionaries and lists.
    :param path_time: str - path to the csv file containing time data
    :return: tuple - a tuple containing lists and dictionaries of relevant time data
    """

    # read csv to dataframe
    df_time= pd.read_csv(path_time) 
    
    # time slot data
    OT = [i+1 for i in df_time.index] # list of time points
    Delta_t = {OT[i]: df_time.loc[i, 'Delta_t'] for i in df_time.index} # time step 
    pt = {OT[i]: df_time.loc[i, 'pt'] for i in df_time.index} # market price of [kw/h]

    return [OT,Delta_t,pt]

def get_data_network(path_bus,path_line,Vnom,Snom):

    """
    Read network data from csv files and return relevant information as dictionaries and lists.
    :param path_bus: str - path to the csv file containing bus data
    :param path_line: str - path to the csv file containing line data
    :return: tuple - a tuple containing lists and dictionaries of relevant network data
    """

    # read csv to dataframe
    df_bus = pd.read_csv(path_bus) # bus data
    df_line= pd.read_csv(path_line) # line data

    # Network Data
    # Buses
    Ob = [df_bus.loc[i,'Nodes'] for i in df_bus.index] # bus indexes

    # Branches
    Ol = {(df_line.loc[i, 'From'], df_line.loc[i, 'To']) for i in df_line.index}  # nodes of lines

    R = {(df_line.loc[i, 'From'], df_line.loc[i, 'To']):
         df_line.loc[i, 'R']/(Vnom ** 2 * 1000 / (Snom))  for i in df_line.index}  # resistance of lines [pu]
    
    X = {(df_line.loc[i, 'From'], df_line.loc[i, 'To']):
         df_line.loc[i, 'X']/(Vnom ** 2 * 1000 / (Snom)) for i in df_line.index}   # reactance of line [pu]
    
    Imax = {(df_line.loc[i, 'From'], df_line.loc[i, 'To']):
            df_line.loc[i, 'Imax']/(Snom/Vnom) for i in df_line.index}  # maximum current [pu]

    Ol = sorted(Ol, key=lambda x: x[0])

    return [Ob,Ol,R,X,Imax]

def get_data_dg(path_dg,Snom):

    """
    Read data about distributed generators (DGs) from csv file and return relevant information as dictionaries and lists.
    :param path_dg: str - path to the csv file containing DG data
    :return: tuple - a tuple containing lists and dictionaries of relevant DG data
    """

    # read csv to dataframe
    df_gen = pd.read_csv(path_dg)

    # Generators - DGs
    Odg = [df_gen.loc[i, 'Nodes'] for i in df_gen.index]      # nodes with DG
    DG_Pmin = {Odg[i]: df_gen.loc[i, 'DG_Pmin']/Snom for i in df_gen.index}     # minimum active power DG [pu]
    DG_Pmax = {Odg[i]: df_gen.loc[i, 'DG_Pmax']/Snom for i in df_gen.index}     # maximum active power DG [pu]
    DG_fp_min = {Odg[i]: df_gen.loc[i, 'DG_fp_min'] for i in df_gen.index}     # minimum power factor DG
    DG_ramp_up = {Odg[i]: df_gen.loc[i, 'DG_ramp_up'] for i in df_gen.index}   # ramp up constraint
    DG_ramp_dw = {Odg[i]: df_gen.loc[i, 'DG_ramp_dw'] for i in df_gen.index} # ramp down constraint
    DG_a = {Odg[i]: df_gen.loc[i, 'DG_a'] for i in df_gen.index}            # quadratic coefficient cost DG

    return [Odg,DG_Pmin,DG_Pmax,DG_fp_min,DG_ramp_up,DG_ramp_dw,DG_a]

def get_data_pv(path_pv,path_time,Snom):

    """
    Read data about photovoltaics (PVs) and time data from csv file and return relevant information as dictionaries and lists.
    :param path_pv: str - path to the csv file containing pv data
    :param path_time: str - path to the csv file containing time data
    :return: tuple - a tuple containing lists and dictionaries of relevant pv data
    """

    # read csv to dataframe
    df_pv  = pd.read_csv(path_pv)
    df_time = pd.read_csv(path_time)

    # PV
    Opv = [df_pv.loc[i, 'Nodes'] for i in df_pv.index]             # nodes with PV
    PV_Pnom = {Ores[i]: df_pv.loc[i, 'PV_Pnom']/ (Snom) for i in df_pv.index}                     # Nominal power PV
    PV_pf = {Ores[i]: df_pv.loc[i, 'PV_pf'] for i in df_pv.index}                         # Power factor PV
    PV_sn = {Ores[i]: df_pv.loc[i, 'PV_sn'] for i in df_pv.index}                         # Per unit subsidy
    PV_Pmin = {Ores[i]: df_pv.loc[i, 'PV_min'] for i in df_pv.index}                     # Minimum power PV
    PV_Pmax = {Ores[i]: df_pv.loc[i, 'PV_max'] for i in df_pv.index}   
    OT = [df_time.loc[i, 'T'] for i in df_time.index]                # list of time points
    G =  {(Opv[i], OT[t]): df_time['PV_{}_{}'.format(df_pv['Nodes'][i],i)][t] for i in df_pv.index for t in df_time.index} # maximum power PV for each hour

    return [Opv,PV_Pnom,PV_Pmin,PV_Pmax,PV_pf,PV_sn,G]

def get_data_cons(path_con,path_time,Snom):

    """
    Read data about consumers and time data from csv file and return relevant information as dictionaries and lists.
    :param path_con: str - path to the csv file containing consumer data
    :param path_time: str - path to the csv file containing time data
    :return: tuple - a tuple containing lists and dictionaries of relevant pv data
    """

    # read csv to dataframe
    df_con  = pd.read_csv(path_con)
    df_time = pd.read_csv(path_time)

    # consumers 
    Ocons = [i+1 for i in df_con.index]                                       # index of consumers
    CONS_nodes = {(Ocons[i], df_con.loc[i, 'Nodes']) for i in df_con.index} # nodes with consumers
    CONS_Pmin = {Ocons[i]: df_con.loc[i, 'CONS_Pmin'] for i in df_con.index}  # minimum power consumers [mw]
    CONS_Pmax = {Ocons[i]: df_con.loc[i, 'CONS_Pmax'] for i in df_con.index}  # maximum power consumers [mw]
    CONS_an = {Ocons[i]: df_con.loc[i, 'CONS_an'] for i in df_con.index}      # instantaneous cost load shifted
    CONS_bn = {Ocons[i]: df_con.loc[i, 'CONS_bn'] for i in df_con.index}      # extra cost load unsatisfied
    PD = {Ocons[i]: df_con.loc[i, 'PDn']/Snom for i in df_con.index}               # nominal nodal active demand in pu
    QD = {Ocons[i]: df_con.loc[i, 'QDn']/Snom  for i in df_con.index}              # nominal nodal reactive demand in pu
    CONS_pf = {Ocons[i]: df_con.loc[i, 'CONS_pf'] for i in df_con.index}      # minimum power factor for consumers
    
    # Demand for consumers
    OT = [df_time.loc[i, 'T'] for i in df_time.index] # list of time points
    PM = {(Ocons[i], OT[t]): df_time['PD_{}_{}'.format(df_con['Nodes'][i],i)][t]/Snom for i in df_con.index for t in df_time.index} # active power demand [mW]
    QM = {(Ocons[i], OT[t]): df_time['QD_{}_{}'.format(df_con['Nodes'][i],i)][t]/Snom for i in df_con.index for t in df_time.index} # reactive power demand [mW]

    CONS_nodes = sorted(CONS_nodes, key=lambda x: x[0])

    return [Ocons,CONS_nodes,CONS_Pmin,CONS_Pmax,CONS_pf,CONS_an,CONS_bn,PM,QM,PD,QD]

def get_data_ess(path_ess,Snom):

    """
    Read data about energy storages (ESS) from csv file and return relevant information as dictionaries and lists.
    :param path_ess: str - path to the csv file containing ess data
    :return: tuple - a tuple containing lists and dictionaries of relevant ESS data
    """

    # read csv to dataframe
    df_ess = pd.read_csv(path_ess)

    # Energy storage systems (ESS)
    Oess = [df_ess.loc[i, 'ESS_node'] for i in df_ess.index]                              # nodes with ESS
    ESS_Pnom = {Oess[i]: df_ess.loc[i, 'ESS_Pnom']/Snom for i in df_ess.index}                 # maximum power ESS
    ESS_Pmin = {Oess[i]: df_ess.loc[i, 'ESS_Pmin'] for i in df_ess.index}                 # minimum power ESS
    ESS_Pmax = {Oess[i]: df_ess.loc[i, 'ESS_Pmax'] for i in df_ess.index}                 # maximum power ESS
    ESS_pf_min = {Oess[i]: df_ess.loc[i, 'ESS_pf_min'] for i in df_ess.index}             # minimum power factor ESS
    ESS_EC = {Oess[i]: df_ess.loc[i, 'ESS_EC']/Snom for i in df_ess.index}                     # energy capacity ESS
    ESS_SOC_ini = {Oess[i]: df_ess.loc[i, 'ESS_SOC_ini']/100 for i in df_ess.index}       # initial state of charge ESS
    ESS_SOC_end = {Oess[i]: df_ess.loc[i, 'ESS_SOC_end']/100 for i in df_ess.index}       # end state of charge ESS
    ESS_dn = {Oess[i]: df_ess.loc[i, 'ESS_dn'] for i in df_ess.index}                     # battery  degradation cost ESS
    ESS_SOC_min = {Oess[i]: df_ess.loc[i, 'SOC_min']/100 for i in df_ess.index}           # minimum state of charge ESS
    ESS_SOC_max = {Oess[i]: df_ess.loc[i, 'SOC_max']/100 for i in df_ess.index}           # maximum state of charge ESS

    return [Oess,ESS_Pmin,ESS_Pmax,ESS_pf_min,ESS_EC,ESS_SOC_ini,ESS_SOC_end,ESS_dn,ESS_SOC_min,ESS_SOC_max]


def get_data_ev(path_ev,Snom):

    # read csv to dataframe
    df_ev = pd.read_csv(path_ev)

    # Electric vehicles (EV)
    Oev = [i+1 for i in df_ev.index]                                      # Index EVs
    EV_nodes = {(i,df_ev.loc[i-1, 'EV_node']) for i in Oev}                                      # Nodes with EVs
    EV_Pmin = {i:df_ev.loc[i-1, 'EV_Pmin'] for i in Oev}                                  # Minimum power EVs
    EV_Pmax = {i:df_ev.loc[i-1, 'EV_Pmax'] for i in Oev}                                # Maximum power EVs
    EV_Pnom = {i:df_ev.loc[i-1, 'EV_Pnom']/Snom for i in Oev}                               # Nominal power EVs
    EV_pf_min = {i:df_ev.loc[i-1, 'EV_pf_min'] for i in Oev}                              # Minimum power factor EVs
    EV_EC = {i:df_ev.loc[i-1, 'EV_EC']/Snom for i in Oev}                                      # Energy capacity EVs
    EV_SOC_ini = {i:df_ev.loc[i-1, 'EV_SOC_ini']/100 for i in Oev}                            # Arrive state of charge
    EV_SOC_end = {i:df_ev.loc[i-1, 'EV_SOC_end']/100 for i in Oev}                            # Departure state of charge
    EV_SOC_min = {i: df_ev.loc[i-1, 'EV_SOC_min']/100 for i in Oev}                        # Minimum state of charge ESS
    EV_SOC_max = {i: df_ev.loc[i-1, 'EV_SOC_max']/100 for i in Oev}                        # Maximum state of charge ESS
    EV_dn = {i:df_ev.loc[i-1, 'EV_dn'] for i in Oev}                                      # Battery  degradation cost
    EV_wn = {i:df_ev.loc[i-1, 'EV_wn'] for i in Oev}                                      # Penalty  cost  for  not  having  their  battery  charged  at  the desired level
    t_arr = {i:df_ev.loc[i-1, 't_arr'] for i in Oev}                                      # Time of arrival
    t_dep = {i:df_ev.loc[i-1, 't_dep'] for i in Oev}                                      # Time of departure

    EV_nodes = sorted(EV_nodes, key=lambda x: x[0])

    return [Oev,EV_nodes,EV_Pmin,EV_Pmax,EV_Pnom,EV_pf_min,EV_EC,EV_SOC_ini,EV_SOC_end,EV_SOC_min,EV_SOC_max,EV_dn,EV_wn,t_arr,t_dep]


def get_themal_model_dat():

    Ac = np.array([[4.37330098e-01, 3.04288766e-04, 3.66367916e-01],
       [4.46803757e-01, 3.10884493e-04, 3.62454328e-01],
       [1.01565609e-02, 6.84308029e-06, 6.59143094e-01]])
    
    Bc = np.array([[1.95997697e-01, 1.66178954e+01, 8.36434986e-01],
       [1.90431031e-01, 9.63215297e+02, 8.22179665e-01],
       [3.30693502e-01, 1.50350574e-01, 7.75926332e-03]])
    
    result = pyreadr.read_r(path=r'C:\Users\Dell\Documents\GitHub\PINNS_OPF\opf\data\raw\Exercise3.RData')
    input_df = result['AllDat']
    U = np.array([input_df['Ta'].to_numpy(),input_df['Gv'].to_numpy(),input_df['Ph1'].to_numpy()])

    initial_Ti = 20
    initial_Tim = 17
    initial_Tom = 12

    return Ac,Bc,U