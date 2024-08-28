import pandas as pd
import numpy as np
import pyomo.environ as pyo
import matplotlib.pyplot as plt
import io
import re
from contextlib import redirect_stdout

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

# Create a list to hold the results
results = []

# Loop over all combinations of Cuts and each setting in tweak_settings
for a in range(0, 4):  # Cuts range from -1 to 3
    for b in range(0, 2):
        for c in range(0, 2):
            for d in range(0, 2):
                for e in range(0, 2):
                    for ff in range(0, 2):
                        for g in range(1, 3):
                            for h in range(0, 3):
                                for i in range(0, 2):
                                    print(a,b,c,d,e,ff,g,h,i)

                                    def unit_commitment_simple(gen_df, loads, gen_variable, mip_gap):
                                        model = pyo.ConcreteModel()

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

                                        model.G = pyo.Set(initialize=G)
                                        model.T = pyo.Set(initialize=T)
                                        model.G_thermal = pyo.Set(initialize=G_thermal)
                                        model.G_nonvar = pyo.Set(initialize=G_nonvar)
                                        model.G_var = pyo.Set(initialize=G_var)
                                        model.G_nt_nonvar = pyo.Set(initialize=G_nt_nonvar)
                                        model.T_red = pyo.Set(initialize=T_red)

                                        # Decision variables
                                        model.GEN = pyo.Var(model.G, model.T, within=pyo.NonNegativeReals)
                                        model.COMMIT = pyo.Var(model.G_thermal, model.T, within=pyo.Binary)
                                        model.START = pyo.Var(model.G_thermal, model.T, within=pyo.Binary)
                                        model.SHUT = pyo.Var(model.G_thermal, model.T, within=pyo.Binary)

                                        # Objective function
                                        def objective_function(model):
                                            return sum((gen_df.loc[gen_df['r_id'] == i, 'heat_rate_mmbtu_per_mwh'].values[0] * 
                                                        gen_df.loc[gen_df['r_id'] == i, 'fuel_cost'].values[0] +
                                                        gen_df.loc[gen_df['r_id'] == i, 'var_om_cost_per_mwh'].values[0]) * model.GEN[i, t]
                                                    for i in model.G_nonvar for t in model.T) + \
                                                sum(gen_df.loc[gen_df['r_id'] == i, 'var_om_cost_per_mwh'].values[0] * model.GEN[i, t]
                                                    for i in model.G_var for t in model.T) + \
                                                sum(gen_df.loc[gen_df['r_id'] == i, 'start_cost_per_mw'].values[0] *
                                                    gen_df.loc[gen_df['r_id'] == i, 'existing_cap_mw'].values[0] *
                                                    model.START[i, t]
                                                    for i in model.G_thermal for t in model.T)

                                        model.obj = pyo.Objective(rule=objective_function, sense=pyo.minimize)

                                        # Demand balance constraint
                                        def demand_balance_rule(model, t):
                                            return sum(model.GEN[i, t] for i in model.G) == loads.loc[loads['hour'] == t, 'demand'].values[0]
                                        
                                        model.demand_balance = pyo.Constraint(model.T, rule=demand_balance_rule)

                                        # Capacity constraints
                                        def cap_thermal_min_rule(model, i, t):
                                            return model.GEN[i, t] >= model.COMMIT[i, t] * gen_df.loc[gen_df['r_id'] == i, 'existing_cap_mw'].values[0] * \
                                                gen_df.loc[gen_df['r_id'] == i, 'min_power'].values[0]
                                        
                                        def cap_thermal_max_rule(model, i, t):
                                            return model.GEN[i, t] <= model.COMMIT[i, t] * gen_df.loc[gen_df['r_id'] == i, 'existing_cap_mw'].values[0]
                                        
                                        def cap_nt_nonvar_rule(model, i, t):
                                            return model.GEN[i, t] <= gen_df.loc[gen_df['r_id'] == i, 'existing_cap_mw'].values[0]
                                        
                                        def cap_var_rule(model, idx):
                                            i = gen_var_cf.iloc[idx]['r_id']
                                            t = gen_var_cf.iloc[idx]['hour']
                                            return model.GEN[i, t] <= gen_var_cf.iloc[idx]['cf'] * gen_var_cf.iloc[idx]['existing_cap_mw']
                                        
                                        model.cap_thermal_min = pyo.Constraint(model.G_thermal, model.T, rule=cap_thermal_min_rule)
                                        model.cap_thermal_max = pyo.Constraint(model.G_thermal, model.T, rule=cap_thermal_max_rule)
                                        model.cap_nt_nonvar = pyo.Constraint(model.G_nt_nonvar, model.T, rule=cap_nt_nonvar_rule)
                                        model.cap_var = pyo.Constraint(range(len(gen_var_cf)), rule=cap_var_rule)

                                        # Unit commitment constraints
                                        def startup_rule(model, i, t):
                                            return model.COMMIT[i, t] >= sum(model.START[i, tt]
                                                                            for tt in set(model.T).intersection(range(t - gen_df.loc[gen_df['r_id'] == i, 'up_time'].values[0], t + 1)))
                                        
                                        def shutdown_rule(model, i, t):
                                            return 1 - model.COMMIT[i, t] >= sum(model.SHUT[i, tt]
                                                                                for tt in set(model.T).intersection(range(t - gen_df.loc[gen_df['r_id'] == i, 'down_time'].values[0], t + 1)))
                                        
                                        def commitment_status_rule(model, i, t):
                                            return model.COMMIT[i, t + 1] - model.COMMIT[i, t] == model.START[i, t + 1] - model.SHUT[i, t + 1]
                                        
                                        model.startup = pyo.Constraint(model.G_thermal, model.T, rule=startup_rule)
                                        model.shutdown = pyo.Constraint(model.G_thermal, model.T, rule=shutdown_rule)
                                        model.commitment_status = pyo.Constraint(model.G_thermal, model.T_red, rule=commitment_status_rule)

                                        # Solve the model
                                        
                                        solver = pyo.SolverFactory('gurobi')
                                        #solver = pyo.SolverFactory('cbc')
                                        #solver = pyo.SolverFactory('glpk')

                                        #----------------------------------------------------------------------------
                                        # Setting Gurobi cut options
                                        # solver.options['Cuts'] = 0  # Moderate aggressiveness
                                        # solver.options['CliqueCuts'] = 2  # Enable clique cuts
                                        # solver.options['GomoryPasses'] = 0
                                        # solver.options['FlowCovers'] = 2  # Enable flow cover cuts
                                        # solver.options['GomoryPasses'] = 5  # Set number of Gomory cut passes
                                        # solver.options['CutPasses'] = 10  # Set the total number of cut passes
                                        #----------------------------------------------------------------------------

                                        # Set the solver options
                                        solver.options['Cuts'] = a
                                        solver.options['CoverCuts'] = b
                                        solver.options['FlowCoverCuts'] = c
                                        solver.options['LiftProjectCuts'] = d
                                        solver.options['MIRCuts'] = e
                                        solver.options['RelaxLiftCuts'] = ff
                                        solver.options['SubMIPCuts'] = g
                                        solver.options['CutPasses'] = h
                                        solver.options['GomoryPasses'] = i

                                        # solver.options[setting] = j

                                        '''
                                        #----------------------------------------------------------------------------
                                        # Adding a custom cut
                                        def custom_cut_rule(model, t):
                                            # This cut ensures the sum of generation is at least 110% of demand during peak hours
                                            return sum(model.GEN[i, t] for i in model.G) >= 1.1 * loads.loc[loads['hour'] == t, 'demand'].values[0]

                                        model.custom_cut = pyo.Constraint(model.T, rule=custom_cut_rule)
                                        #----------------------------------------------------------------------------
                                        '''

                                        solver.options['mipgap'] = mip_gap

                                        # Capture the solver log output
                                        f = io.StringIO()
                                        with redirect_stdout(f):
                                            results = solver.solve(model, tee=True)
                                        
                                        log_output = f.getvalue()

                                        # Use regex to extract the MIP gap from the solver log
                                        mip_gap_value = None
                                        gap_match = re.search(r"gap\s+(\d+\.\d+)%", log_output.lower())
                                        if gap_match:
                                            mip_gap_value = float(gap_match.group(1))

                                        # Generation solution and convert to data frame
                                        gen = value_to_df_2dim([[pyo.value(model.GEN[i, t]) for t in model.T] for i in model.G], [model.G, model.T])

                                        # Commitment status solution and convert to data frame
                                        commit = value_to_df_2dim([[pyo.value(model.COMMIT[i, t]) for t in model.T] for i in model.G_thermal], [model.G_thermal, model.T])

                                        # Calculate curtailment
                                        curtail = pd.merge(gen_var_cf, gen, on=['r_id', 'hour'])
                                        curtail['curt'] = curtail['cf'] * curtail['existing_cap_mw'] - curtail['gen']

                                        '''
                                        # Extract the MIP gap value
                                        # mip_gap_value = results['Problem'][0]['MIPGap'] if 'MIPGap' in results['Problem'][0] else None
                                        '''
                                        
                                        return {
                                            "gen": gen,
                                            "commit": commit,
                                            "curtail": curtail,
                                            "cost": pyo.value(model.obj),
                                            "mip_gap": mip_gap_value,
                                            "status": results.solver.termination_condition
                                        }

                                    # Run the unit commitment model
                                    n = 100
                                    T_period = range(n * 24 + 1, (n + 1) * 24 + 1)

                                    # High solar case: 3,500 MW
                                    gen_df_sens = gen_df.copy()
                                    gen_df_sens.loc[gen_df_sens['resource'] == "solar_photovoltaic", 'existing_cap_mw'] = 2000

                                    loads_multi = loads[loads['hour'].isin(T_period)]
                                    gen_variable_multi = gen_variable_long[gen_variable_long['hour'].isin(T_period)]

                                    solution = unit_commitment_simple(gen_df_sens, loads_multi, gen_variable_multi, 0.01)

                                    # Extract the MIP gap from the results
                                    mip_gap_value = solution.get('mip_gap', None)

                                    '''
                                    # Create the CSV content
                                    csv_content = {
                                        "Cuts": [0],
                                        "Setting": ["None"],
                                        "Value": [0],
                                        "Gap": [mip_gap_value]
                                    }

                                    # Convert to a DataFrame
                                    csv_df = pd.DataFrame(csv_content)

                                    # Write the DataFrame to a CSV file
                                    csv_df.to_csv("first_test_model_gurobi_settings_results.csv", index=False)
                                    '''

                                    print(mip_gap_value)
                                    
                                    # Add the result to the results list
                                    results.append([a,b,c,d,e,ff,g,h,i, mip_gap_value])

# Convert the results to a DataFrame
results_df = pd.DataFrame(results, columns=["Cuts", "CoverCuts", "FlowCoverCuts", "LiftProjectCuts", "MIRCuts", "RelaxLiftCuts", "SubMIPCuts", "CutPasses", "GomoryPasses", "Gap"])

# Write the results to a CSV file
results_df.to_csv("solver_tuning_results_example3_phase2.csv", index=False)

print("Experiment completed.")