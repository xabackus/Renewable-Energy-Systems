import pyomo.environ as pyo
import solver
# Example of Creating and Solving a Model


# Define model
model = pyo.ConcreteModel()
# Time periods (hours in a day)
hours = list(range(24))
# Thermal units
units = ['Unit1', 'Unit2', 'Unit3']
max_output = {'Unit1': 100, 'Unit2': 150, 'Unit3': 200}
min_output = {'Unit1': 30, 'Unit2': 50, 'Unit3': 75}
startup_cost = {'Unit1': 1000, 'Unit2': 1500, 'Unit3': 2000}
operating_cost = {'Unit1': 20, 'Unit2': 25, 'Unit3': 30}  # Cost per MWh
# Wind generation forecast (MWh)
wind_forecast = [20, 15, 30, 25, 20, 15, 10, 30, 40, 35, 30, 25, 20, 15, 30, 25, 20, 15, 10, 30, 40, 35, 30, 25]
# Demand (MWh)
demand = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330]
# Variables
model.commitment = pyo.Var(units, hours, within=pyo.Binary)  # 1 if unit is on, 0 otherwise
model.generation = pyo.Var(units, hours, within=pyo.NonNegativeReals)
# Objective: Minimize total cost
def objective_rule(model):
    return sum(model.commitment[u, h] * startup_cost[u] + model.generation[u, h] * operating_cost[u] for u in units for h in hours)
model.cost = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
# Constraints
# Demand fulfillment
def demand_constraint_rule(model, h):
    return sum(model.generation[u, h] for u in units) + wind_forecast[h] >= demand[h]
model.demand_constraint = pyo.Constraint(hours, rule=demand_constraint_rule)
# Lower generation limit
def generation_lower_limit_rule(model, u, h):
    return model.generation[u, h] >= min_output[u] * model.commitment[u, h]
model.generation_lower_limit = pyo.Constraint(units, hours, rule=generation_lower_limit_rule)
# Upper generation limit
def generation_upper_limit_rule(model, u, h):
    return model.generation[u, h] <= max_output[u] * model.commitment[u, h]
model.generation_upper_limit = pyo.Constraint(units, hours, rule=generation_upper_limit_rule)

# Example Usage
solve_status = solver.solve_milp(model, 'gurobi', 'gurobi_example_solution.csv','pyomo')
solve_status = solver.solve_milp(model, 'glpk', 'glpk_example_solution.csv','pyomo')
solve_status = solver.solve_milp(model, 'cbc', 'cbc_example_solution.csv','pyomo')
solve_status = solver.solve_milp('/Users/xanderbackus/example_model.mps', 'gurobi', 'gurobi_mps_example_solution.csv','mps')
#solve_status = solver.solve_milp('/Users/xanderbackus/instances/1_item_placement/train/item_placement_0.mps', 'gurobi', 'gurobi_mps_example_solution2.csv','mps')
solve_status = solver.solve_milp('/Users/xanderbackus/unit_commitment.mps', 'gurobi', 'gurobi_mps_example_solution3.csv','mps')
