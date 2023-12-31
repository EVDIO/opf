from pyomo.environ import *
from .data_opf import get_data_time,get_data_network,get_data_dg,get_data_pv,get_data_cons,get_data_ess,get_data_ev


def param_var_time(model,path_time):

    """
    Sets the time slot data for the optimization model.

    Args:
        model: Pyomo abstract model object
        path_time (str): Path to the time slot data file

    Returns:
        Pyomo abstract model object with time slot data set as parameters
    """

    # Get time slot data
    OT,Delta_t,pt = get_data_time(path_time)

    # Set time nodes
    model.OT = Set(initialize=OT)

    # Parameters
    model.Delta_t = Param(model.OT, initialize=Delta_t, mutable=False)  # time interval
    model.pt = Param(model.OT, initialize=pt, mutable=False)  # wholesale market price
    
    return model

def param_var_dg(model,path_dg,Snom):
    
    """
    Sets the generator data for the optimization model.

    Args:
        model: Pyomo abstract model object
        path_dg (str): Path to the generator data file

    Returns:
        Pyomo abstract model object with generator data set as parameters and variables
    """

    # Get generator data
    Odg,DG_nodes,DG_Pnom,DG_Pmin,DG_Pmax,DG_fp_min,DG_ramp_up,DG_ramp_dw,DG_a = get_data_dg(path_dg,Snom)

    # Set generator nodes
    model.Odg = Set(initialize=Odg)
    model.DG_nodes = Set(initialize=DG_nodes)

    # Parameters
    model.DG_Pnom = Param(model.Odg, initialize=DG_Pnom, mutable=False)  # minimum power DGs
    model.DG_Pmin = Param(model.Odg, initialize=DG_Pmin, mutable=False)  # minimum power DGs
    model.DG_Pmax = Param(model.Odg, initialize=DG_Pmax, mutable=False)  # maximum power DGs
    model.DG_fp_min = Param(model.Odg, initialize=DG_fp_min, mutable=False)  # minimum power factor DGs
    model.DG_ramp_up = Param(model.Odg, initialize=DG_ramp_up, mutable=False)  # ramp up constraint
    model.DG_ramp_dw = Param(model.Odg, initialize=DG_ramp_dw, mutable=False)  # ramp down constraint
    model.DG_a = Param(model.Odg, initialize=DG_a, mutable=False)  # quadratic coefficient cost DGs

    # Variables
    model.dg_x =  Var(model.Odg, model.OT, initialize=1.0, within=NonNegativeReals, bounds=(0, 1))  # decision variable for active power of generators (0,1)
    model.Qdg = Var(model.Odg, model.OT,initialize=0.0, within=Reals) # reactive power for DGs 
    model.DG_cost = Var(model.Odg, initialize=1.0, within=NonNegativeReals)    # cost DGs

    return model

def param_var_con(model,path_con,path_time,Snom):

    """
    Sets the consumer data for the optimization model.

    Args:
        model: Pyomo abstract model object
        path_con (str): Path to the consumer data file
        path_time (str): Path to the time slot data file

    Returns:
        Pyomo abstract model object with consumer data set as parameters and variables
    """

    # Get consumer data
    Ocons,CONS_nodes,CONS_Pmin,CONS_Pmax,CONS_pf,CONS_an,CONS_bn,PM,QM,PD,QD = get_data_cons(path_con, path_time, Snom)

    # Set nodes
    model.Ocons = Set(initialize=Ocons)
    model.CONS_nodes = Set(initialize=CONS_nodes)

    # Parameters 
    model.CONS_Pmin = Param(model.Ocons, initialize=CONS_Pmin, mutable=False)  # Minimum power CONS
    model.CONS_Pmax = Param(model.Ocons, initialize=CONS_Pmax, mutable=False)  # Maximum power CONS
    model.CONS_pf = Param(model.Ocons, initialize=CONS_pf, mutable=False)  # Constant power factor CONS
    model.PM = Param(model.Ocons,model.OT, initialize=PM, mutable=False) # Active power demand for CONS
    model.CONS_an = Param(model.Ocons, initialize=CONS_an, mutable=False)  # quadratic component cost CONS

    # Variables
    model.cons_x = Var(model.Ocons, model.OT, initialize=1.0, within=NonNegativeReals,bounds=(0, 1))    # Multiplier demands CONSUMERS (0,1)
    model.Qcons = Var(model.Ocons, model.OT,initialize=1.0, within=NonNegativeReals) # Reactive power for CONSUMERS
    model.CONS_cost = Var(model.Ocons, initialize=1.0, within=NonNegativeReals) 

    model.Ti = Var(model.Ocons, initialize=20.0, bounds = (5,35))

    return model

def param_var_pv(model,path_pv,path_time, Snom):
        
    """
    Sets the pv data for the optimization model.

    Args:
        model: Pyomo abstract model object
        path_con (str): Path to the pv data file
        path_time (str): Path to the time slot data file

    Returns:
        Pyomo abstract model object with pv data set as parameters and variables
    """

    # Get pv data
    Opv,PV_nodes,PV_Pnom,PV_Pmin,PV_Pmax,PV_pf,PV_sn,G = get_data_pv(path_pv, path_time, Snom)
    
    model.Opv = Set(initialize=Opv)
    model.PV_nodes = Set(initialize=PV_nodes)


    model.PV_Pmax = Param(model.Opv, initialize=PV_Pmax, mutable=False) # Maximum active power PV
    model.PV_Pmin = Param(model.Opv, initialize=PV_Pmin, mutable=False)  # Minimum power PVs
    model.PV_pf = Param(model.Opv, initialize=PV_pf, mutable=False)  # Constant power factor PVs
    model.G = Param(model.Opv, model.OT, initialize=G, mutable=False) # Maximum active power for PVs 
    model.PV_sn = Param(model.Opv, initialize=PV_sn, mutable=False)  # Compensation PV

    model.pv_x = Var(model.Opv, model.OT, initialize=1.0, within=NonNegativeReals,bounds=(0, 1))    # Multiplier demands PV (0,1)
    model.Qpv = Var(model.Opv, model.OT,initialize=1.0, within=Reals)
    model.PV_cost = Var(model.Opv, initialize=1.0,within=NonNegativeReals)    

    return model

def param_var_ess(model,path_ess, Snom):

    """
    Sets the energy storage system data for the optimization model.

    Args:
        model: Pyomo abstract model object
        path_dg (str): Path to the energy storage system data file

    Returns:
        Pyomo abstract model object with energy storage system data set as parameters and variables
    """

    # Get ESS data
    Oess,ESS_nodes,ESS_Pnom,ESS_Pmin,ESS_Pmax,ESS_pf_min,ESS_EC,ESS_SOC_ini,ESS_SOC_end,ESS_dn,ESS_SOC_min,ESS_SOC_max = get_data_ess(path_ess,Snom)


    model.Oess = Set(initialize=Oess)
    model.ESS_nodes = Set(initialize=ESS_nodes)
    
    # Parameters
    model.ESS_Pmin = Param(model.Oess, initialize=ESS_Pmin, mutable=False)  # Minimum power ESS
    model.ESS_Pmax = Param(model.Oess, initialize=ESS_Pmax, mutable=False)  # Maximum power ESS
    model.ESS_pf_min = Param(model.Oess, initialize=ESS_pf_min, mutable=False)  # Minimum power factor ESS
    model.ESS_SOC_end = Param(model.Oess, initialize=ESS_SOC_end, mutable=False)  # Final state of charge ESS
    model.ESS_SOC_ini = Param(model.Oess, initialize=ESS_SOC_ini, mutable=False)  # Initial state of charge ESS
    model.ESS_SOC_min = Param(model.Oess, initialize=ESS_SOC_min, mutable=False)  # Minimum state of charge ESS
    model.ESS_SOC_max = Param(model.Oess, initialize=ESS_SOC_max, mutable=False)  # MAximum state of charge ESS
    model.ESS_dn = Param(model.Oess, initialize=ESS_dn, mutable=False)  # Depretiation cost ESS
    model.ESS_EC = Param(model.Oess, initialize=ESS_EC, mutable=False)  # Energy capacity ESS
    
    # Variables 
    model.ess_x = Var(model.Oess, model.OT, initialize=1.0, within=NonNegativeReals,bounds=(0, 1))    # Multiplier demands PV (0,1)
    model.Qess = Var(model.Oess,model.OT, initialize=0.0, within=Reals) 
    model.SOC = Var(model.Oess,model.OT, initialize=1.0, within=NonNegativeReals)    # Reactive power from ESS
    model.ESS_cost = Var(model.Oess, initialize=1.0, within=NonNegativeReals)    # Reactive power from ESS

    return model

def param_var_ev(model,path_ev, Snom):

    Oev,EV_nodes,EV_Pmin,EV_Pmax,EV_Pnom,EV_pf_min,EV_EC,EV_SOC_ini,EV_SOC_end,EV_SOC_min,EV_SOC_max,EV_dn,EV_wn,t_arr,t_dep = get_data_ev(path_ev, Snom)

    model.Oev = Set(initialize=Oev)
    model.EV_nodes = Set(initialize=EV_nodes)

    # EVs
    model.EV_SOC_end = Param(model.Oev, initialize=EV_SOC_end, mutable=False)  # Departure SOC EV
    model.EV_SOC_ini = Param(model.Oev, initialize=EV_SOC_ini, mutable=False)  # Arrival SOC EV
    model.EV_wn = Param(model.Oev, initialize=EV_wn, mutable=False)  # Cost EV
    model.EV_pf_min = Param(model.Oev, initialize=EV_pf_min, mutable=False)  # Minimum power factor EV
    model.EV_dn = Param(model.Oev, initialize=EV_dn, mutable=False)  # Cost  EV
    model.EV_Pmax = Param(model.Oev, initialize=EV_Pmax, mutable=False)  # Maximum power EV
    model.EV_Pmin = Param(model.Oev, initialize=EV_Pmin, mutable=False)  # Minimum power EV
    model.EV_Pnom = Param(model.Oev, initialize=EV_Pnom, mutable=False)  # Nominal power EV
    model.EV_EC = Param(model.Oev, initialize=EV_EC, mutable=False)  # Energy capacity EV
    model.EV_SOC_min = Param(model.Oev, initialize=EV_SOC_min, mutable=False)  # Energy capacity EV
    model.EV_SOC_max = Param(model.Oev, initialize=EV_SOC_max, mutable=False)  # Energy capacity EV
    model.t_arr = Param(model.Oev, initialize=t_arr, mutable=False)  # Energy capacity EV
    model.t_dep = Param(model.Oev, initialize=t_dep, mutable=False)  # Energy capacity EV

    model.Pev = Var(model.Oev, model.OT, initialize=0.0)    # Active power from EV
    model.Qev = Var(model.Oev, model.OT, initialize=0.0)    # Active power from EV
    model.SOC_EV = Var(model.Oev, model.OT, initialize=0.0)    # SOC from EV
    model.E_non_served = Var(model.Oev, initialize=0.0, within=NonNegativeReals)    # SOC from EV
    model.EV_cost = Var(model.Oev, initialize=1.0)    # SOC from EV

    return model

def param_var_network(model,path_bus,path_line, Vnom, Snom, Vmin, Vmax):

    """
    Sets the network data for the optimization model.

    Args:
        model: Pyomo abstract model object
        path_bus (str): Path to the bus data file
        path_line (str): Path to the line data file

    Returns:
        Pyomo abstract model object with network data set as parameters and variables
    """
    
    Ob,Tb,Ol,R,X,Imax = get_data_network(path_bus,path_line,Vnom, Snom)
    
    # define Sets
    model.Ob = Set(initialize=Ob)
    model.Tb = Set(initialize=Tb)
    model.Ol = Set(initialize=Ol)
    
    # Define Parameters
    model.Vnom = Param(initialize=Vnom, mutable=False)   # Base voltage magnitude
    model.Snom = Param(initialize=Snom, mutable=False)   # Base apparent power
    model.Vmin = Param(initialize=Vmin, mutable=False)   # Minimum voltage magnitude
    model.Vmax = Param(initialize=Vmax, mutable=False)   # Maximum voltage magnitude
    model.R = Param(model.Ol, initialize=R, mutable=False) # line resistance
    model.X = Param(model.Ol, initialize=X, mutable=False) # line reactance
    model.Imax = Param(model.Ol, initialize=Imax, mutable=False) # maximum current magnitude

    # define variables
    model.P = Var(model.Ol, model.OT, initialize=0, within=NonNegativeReals) # acive power flowing in lines
    model.Q = Var(model.Ol, model.OT, initialize=0, within=Reals) # reacive power flowing in lines
    model.I  = Var(model.Ol, model.OT, initialize=0, within=NonNegativeReals) # current of lines
    model.V = Var(model.Ob, model.OT, initialize=0.0, within=NonNegativeReals) # voltage in bus

    return model



def param_var_temp(model):
    Ri = 46.848    # Resistance between indoor air and interior walls
    Rim = 1.809    # Resistance between indoor air and house envelop
    Ra = 8.021     # Resistance between indoor air and outdoor
    Ram = 0.0846   # Resistance between house envelope and outdoor

    Ci = 8.120      # heat capacity of indoor air
    Cim = 0.00553   # heat capacity of interior walls
    Com = 292.905   # heat capacity of house envelope

    Ap = 20.212     # window area
    p = 1          # fraction


    # Define the matrices A and B
    A = {
    (1, 1): -1/(Ci) - 1/(Ci * Ra) - 1/(Ci * Ri) - 1/(Ci * Rim),
    (2, 1): 1/(Cim * Ri),
    (3, 1): Com * Rim,
    (1, 2): 0.0,
    (2, 2): -1/(Cim * Ri),
    (3, 2): 0.0,
    (1, 3): 0.0,
    (2, 3): 0.0,
    (3, 3): -1/(Com * Rim) - 1/(Com * Ram)
    }

    B = {
    (1, 1): 1/(Ci * Ra),
    (1, 2): Ap * (1 - p) / Ci,
    (1, 3): 1/Ci,
    (2, 1): 0.0,
    (2, 2): Ap * p / Cim,
    (2, 3): 0.0,
    (3, 1): 1/(Com * Ram),
    (3, 2): 0.0,
    (3, 3): 0.0
    }

    k = [1,2,3]
    # define Sets
    model.k = Set(initialize=k)

    model.A = Param(model.k*model.k, initialize=A, mutable=False)   
    model.B = Param(model.k*model.k, initialize=B, mutable=False)  

    # Define the variables
    model.x = Var(model.Ocons,model.OT,k,initialize=1.0, within=Reals)
    model.u = Var(model.Ocons,model.OT,k,initialize=1.0, within=Reals)

    return model