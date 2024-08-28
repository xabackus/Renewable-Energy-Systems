from gurobipy import Model, GRB

# Create a new model
model = Model("example_model")
# Add variables
x = model.addVar(name="x")
y = model.addVar(name="y")

# Set objective
model.setObjective(2 * x + 3 * y, GRB.MAXIMIZE)

# Add constraint
model.addConstr(x + 5 * y <= 10, "constraint1")

# Update model to integrate new variables and constraints
model.update()

# Optimize the model (optional, depending on your need)
model.optimize()

# Write the model to an MPS file
model.write("example_model.mps")

import gurobipy as gp
from gurobipy import GRB

# Define the data for the problem
generators = ['G1', 'G2']
time_periods = [1, 2, 3]
demand = {1: 50, 2: 60, 3: 55}
costs = {'G1': 20, 'G2': 25}
min_power = {'G1': 20, 'G2': 10}
max_power = {'G1': 60, 'G2': 40}
startup_cost = {'G1': 50, 'G2': 40}

# Create a new model
model = gp.Model("unit_commitment")

# Create variables
commitment = model.addVars(generators, time_periods, vtype=GRB.BINARY, name="commitment")
power = model.addVars(generators, time_periods, vtype=GRB.CONTINUOUS, name="power")

# Add constraints
for t in time_periods:
    # Meet demand
    model.addConstr(gp.quicksum(power[g, t] for g in generators) == demand[t], name=f"demand_{t}")
    
    for g in generators:
        # Power generation limits
        model.addConstr(power[g, t] <= commitment[g, t] * max_power[g], name=f"max_power_{g}_{t}")
        model.addConstr(power[g, t] >= commitment[g, t] * min_power[g], name=f"min_power_{g}_{t}")

# Objective function: Minimize cost
model.setObjective(gp.quicksum(commitment[g, t] * (startup_cost[g] + costs[g] * power[g, t])
                               for g in generators for t in time_periods), GRB.MINIMIZE)

# Optimize model
model.optimize()

# Export the model to an MPS file
model.write("unit_commitment.mps")