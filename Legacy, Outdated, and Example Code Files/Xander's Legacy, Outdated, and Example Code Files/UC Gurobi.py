import pandas as pd
import numpy as np
from gurobipy import Model, GRB
import matplotlib.pyplot as plt

'''
pd.set_option('display.max_rows', None)  # None means show all rows
pd.set_option('display.max_columns', None)  # None means show all columns
pd.set_option('display.width', 1000)  # Adjust the width to fit your display
pd.set_option('display.max_colwidth', None)  # Display full content of each column
'''

datadir = "/Users/xanderbackus/power-systems-optimization-master/Notebooks/uc_data"
gen_info = pd.read_csv(f"{datadir}/Generators_data.csv")
fuels = pd.read_csv(f"{datadir}/Fuels_data.csv")
loads = pd.read_csv(f"{datadir}/Demand.csv")
gen_variable = pd.read_csv(f"{datadir}/Generators_variability.csv")

# Rename all columns to lowercase
for df in [gen_info, fuels, loads, gen_variable]:
    df.columns = df.columns.str.lower()

# Keep columns relevant to our UC model 
gen_info = gen_info.iloc[:, :26]  # columns 1:26
gen_df = pd.merge(gen_info, fuels, on='fuel', how='left')  # load in fuel costs and add to data frame
gen_df['fuel_cost'] = gen_df['cost_per_mmbtu'].fillna(0)

# Create "is_variable" column to indicate if this is a variable generation source (e.g. wind, solar)
gen_df['is_variable'] = gen_df['resource'].isin(['onshore_wind_turbine', 'small_hydroelectric', 'solar_photovoltaic'])

# Create full name of generator (including geographic location and cluster number)
gen_df['gen_full'] = (gen_df['region'] + "_" + gen_df['resource'] + "_" + gen_df['cluster'].astype(str) + ".0").str.lower()

# Remove generators with no capacity (e.g. new build options that we'd use if this was capacity expansion problem)
gen_df = gen_df[gen_df['existing_cap_mw'] > 0]

# Convert from GMT to GMT-8
gen_variable['hour'] = (gen_variable['hour'] - 9) % 8760 + 1
gen_variable = gen_variable.sort_values(by='hour')
loads['hour'] = (loads['hour'] - 9) % 8760 + 1
loads = loads.sort_values(by='hour')

# Convert from "wide" to "long" format
gen_variable_long = gen_variable.melt(id_vars=['hour'], var_name='gen_full', value_name='cf')

def value_to_df_2dim(var, axes):
    data = pd.DataFrame(var, index=axes[0], columns=axes[1])
    data = data.reset_index().melt(id_vars='index', var_name='hour', value_name='gen')
    data.rename(columns={'index': 'r_id'}, inplace=True)
    data['hour'] = data['hour'].astype(int)
    return data

def unit_commitment_simple(gen_df, loads, gen_variable, mip_gap):
    UC = Model("unit_commitment")
    UC.setParam('MIPGap', mip_gap)
    
    # Define sets based on data
    G_thermal = gen_df[gen_df['up_time'] > 0]['r_id'].tolist()
    G_nonthermal = gen_df[gen_df['up_time'] == 0]['r_id'].tolist()
    G_var = gen_df[gen_df['is_variable'] == True]['r_id'].tolist()
    G_nonvar = gen_df[gen_df['is_variable'] == False]['r_id'].tolist()
    G_nt_nonvar = list(set(G_nonvar) & set(G_nonthermal))
    G = gen_df['r_id'].tolist()
    T = loads['hour'].tolist()
    T_red = T[:-1]
    
    gen_var_cf = pd.merge(gen_variable, 
                          gen_df[gen_df['is_variable'] == True][['r_id', 'gen_full', 'existing_cap_mw']], 
                          on='gen_full')

    # Decision variables
    GEN = UC.addVars(G, T, lb=0, vtype=GRB.CONTINUOUS, name="GEN")
    COMMIT = UC.addVars(G_thermal, T, vtype=GRB.BINARY, name="COMMIT")
    START = UC.addVars(G_thermal, T, vtype=GRB.BINARY, name="START")
    SHUT = UC.addVars(G_thermal, T, vtype=GRB.BINARY, name="SHUT")
    
    # Objective function
    UC.setObjective(
        sum((gen_df.loc[gen_df['r_id'] == i, 'heat_rate_mmbtu_per_mwh'].values[0] * 
             gen_df.loc[gen_df['r_id'] == i, 'fuel_cost'].values[0] +
             gen_df.loc[gen_df['r_id'] == i, 'var_om_cost_per_mwh'].values[0]) * GEN[i, t]
            for i in G_nonvar for t in T) +
        sum(gen_df.loc[gen_df['r_id'] == i, 'var_om_cost_per_mwh'].values[0] * GEN[i, t]
            for i in G_var for t in T) +
        sum(gen_df.loc[gen_df['r_id'] == i, 'start_cost_per_mw'].values[0] *
            gen_df.loc[gen_df['r_id'] == i, 'existing_cap_mw'].values[0] *
            START[i, t]
            for i in G_thermal for t in T),
        GRB.MINIMIZE
    )
    
    # Demand balance constraint
    UC.addConstrs(
        (sum(GEN[i, t] for i in G) == loads.loc[loads['hour'] == t, 'demand'].values[0]
         for t in T),
        "cDemand"
    )

    # Capacity constraints
    UC.addConstrs(
        (GEN[i, t] >= COMMIT[i, t] * gen_df.loc[gen_df['r_id'] == i, 'existing_cap_mw'].values[0] *
         gen_df.loc[gen_df['r_id'] == i, 'min_power'].values[0]
         for i in G_thermal for t in T),
        "Cap_thermal_min"
    )
    UC.addConstrs(
        (GEN[i, t] <= COMMIT[i, t] * gen_df.loc[gen_df['r_id'] == i, 'existing_cap_mw'].values[0]
         for i in G_thermal for t in T),
        "Cap_thermal_max"
    )
    UC.addConstrs(
        (GEN[i, t] <= gen_df.loc[gen_df['r_id'] == i, 'existing_cap_mw'].values[0]
         for i in G_nt_nonvar for t in T),
        "Cap_nt_nonvar"
    )
    UC.addConstrs(
        (GEN[gen_var_cf.iloc[i]['r_id'], gen_var_cf.iloc[i]['hour']] <=
         gen_var_cf.iloc[i]['cf'] * gen_var_cf.iloc[i]['existing_cap_mw']
         for i in range(len(gen_var_cf))),
        "Cap_var"
    )
    
    # Unit commitment constraints
    UC.addConstrs(
        (COMMIT[i, t] >= sum(START[i, tt]
                             for tt in set(T).intersection(range(t - gen_df.loc[gen_df['r_id'] == i, 'up_time'].values[0], t + 1)))
         for i in G_thermal for t in T),
        "Startup"
    )
    UC.addConstrs(
        (1 - COMMIT[i, t] >= sum(SHUT[i, tt]
                                 for tt in set(T).intersection(range(t - gen_df.loc[gen_df['r_id'] == i, 'down_time'].values[0], t + 1)))
         for i in G_thermal for t in T),
        "Shutdown"
    )
    UC.addConstrs(
        (COMMIT[i, t + 1] - COMMIT[i, t] == START[i, t + 1] - SHUT[i, t + 1]
         for i in G_thermal for t in T_red),
        "CommitmentStatus"
    )
    
    # Solve the model
    UC.optimize()
    
    # Generation solution and convert to data frame
    gen = value_to_df_2dim([[GEN[i, t].X for t in T] for i in G], [G, T])

    # Commitment status solution and convert to data frame
    commit = value_to_df_2dim([[COMMIT[i, t].X for t in T] for i in G_thermal], [G_thermal, T])

    # Calculate curtailment
    curtail = pd.merge(gen_var_cf, gen, on=['r_id', 'hour'])
    curtail['curt'] = curtail['cf'] * curtail['existing_cap_mw'] - curtail['gen']
    
    return {
        "gen": gen,
        "commit": commit,
        "curtail": curtail,
        "cost": UC.ObjVal,
        "primal_bound": UC.ObjBound,
        "dual_bound": UC.ObjBoundC,
        "status": UC.Status
    }

n = 100
T_period = range(n * 24 + 1, (n + 1) * 24 + 1)

# High solar case: 3,500 MW
gen_df_sens = gen_df.copy()
gen_df_sens.loc[gen_df_sens['resource'] == "solar_photovoltaic", 'existing_cap_mw'] = 3500

loads_multi = loads[loads['hour'].isin(T_period)]
gen_variable_multi = gen_variable_long[gen_variable_long['hour'].isin(T_period)]

solution = unit_commitment_simple(gen_df_sens, loads_multi, gen_variable_multi, 0.01)

def output_to_csv(solution, filename):
    """
    Takes the output from the unit_commitment_simple function, converts it to a CSV file.
    
    Parameters:
        solution (dict): The output dictionary from the unit_commitment_simple Gurobi solver.
        filename (str): The filename where the CSV will be saved.
    """
    # Convert the solution dictionary into a DataFrame
    # This assumes the solution is a dictionary with keys that we want as columns
    # Each key should contain lists or values directly compatible with DataFrame creation
    df = pd.DataFrame({key: [value] if not isinstance(value, list) else value
                       for key, value in solution.items()})
    
    # Write the DataFrame to a CSV file
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

print(solution)

output_to_csv(solution, filename="/Users/xanderbackus/gurobi_output.csv")