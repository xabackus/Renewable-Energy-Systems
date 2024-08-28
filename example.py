#!/usr/bin/env python
import sys

"""Example code to generate and solve UC MILP models"""

import pyomo.environ as pyo
from helpers import parsecase, add_gens_to_case
import pickle
import main as ucml
import pandapower
import pandas as pd
import matplotlib.pyplot as plt
from pyomo.opt import SolverStatus, TerminationCondition

net = pandapower.networks.case_ieee30()
num_solar = int(sys.argv[1])
num_wind = int(sys.argv[2])
num_hydro = int(sys.argv[3])
num_batt = int(sys.argv[4])
num_therm = int(sys.argv[5])

# Usage
add_gens_to_case(net, num_solar, num_wind, num_batt)

# single helper function so that the kwargs are the same
kwargs = {'num_solar': num_solar, 'num_wind':  len(net.sgen) - num_solar, 'num_hydro': 0, 'num_batt': len(net.storage), 'num_therm': len(net.gen), 'num_nodes': len(net.bus), 'num_lines': len(net.line), 'time_periods': 24, 'num_scenarios': 1, 'num_uncert': 1, 'num_demands': len(net.load)}
model_name = "UCModel" + "_".join([key + "=" + str(kwargs[key]) for key in kwargs])
db = parsecase(net, **kwargs, model_name=model_name)
data = pickle.loads(db)
model = ucml.opt_model_generator(**kwargs)
# model.pprint()

instance = model.create_instance(data)
# make into MPS file
instance.write("data/" + model_name + ".mps")

opt = pyo.SolverFactory('gurobi')
result = opt.solve(instance, tee=False)
if result.solver.status == SolverStatus.ok and result.solver.termination_condition == TerminationCondition.optimal:
    if hasattr(result.problem, 'upper_bound') and hasattr(result.problem, 'lower_bound'):
        primal_bound = result.problem.upper_bound
        dual_bound = result.problem.lower_bound
        print("primal bound:", primal_bound)
        print("dual bound:", dual_bound)
        out = {"dual_bound": dual_bound, "primal_bound": primal_bound}
    print("optimal value:", pyo.value(instance.obj))
else:
    print("NO OPTIMAL VALUE FOUND")

# make a file with output json file, with name
num_renew = num_solar + kwargs['num_wind']
num_gen = num_renew + kwargs['num_hydro'] + kwargs['num_batt'] + kwargs['num_therm']
Gsolar = range(1, num_solar + 1)
Gwind = range(num_solar + 1, num_solar + kwargs['num_wind'] + 1)
Ghydro = range(num_renew + 1, num_renew + kwargs['num_hydro'] + 1)
Gbatt = range(num_renew + kwargs['num_hydro'] + 1, num_gen - kwargs['num_therm'] + 1)
Gtherm = range(num_gen - kwargs['num_therm'] + 1, num_gen + 1)
Grenew = range(1, num_renew + 1)    

df = pd.DataFrame({
    'thermal': [sum(pyo.value(instance.p[g, t, s]) for g in Gtherm for s in range(1, kwargs['num_scenarios'] + 1)) for t in range(1, kwargs['time_periods'] + 1)],
    'solar': [sum(pyo.value(instance.p[g, t, s]) for g in Gsolar for s in range(1, kwargs['num_scenarios'] + 1)) for t in range(1, kwargs['time_periods'] + 1)],
    'wind': [sum(pyo.value(instance.p[g, t, s]) for g in Gwind for s in range(1, kwargs['num_scenarios'] + 1)) for t in range(1, kwargs['time_periods'] + 1)],
    'hydro': [sum(pyo.value(instance.p[g, t, s]) for g in Ghydro for s in range(1, kwargs['num_scenarios'] + 1)) for t in range(1, kwargs['time_periods'] + 1)],
    'battery': [sum(pyo.value(instance.p[g, t, s]) for g in Gbatt for s in range(1, kwargs['num_scenarios'] + 1)) for t in range(1, kwargs['time_periods'] + 1)],
    })

ax = df.plot.area(stacked=True)
plt.show()
