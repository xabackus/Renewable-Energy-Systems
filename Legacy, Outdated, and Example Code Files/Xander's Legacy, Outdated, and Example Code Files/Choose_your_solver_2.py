import pandas as pd
import numpy as np
import pyomo.environ as pyo
import matplotlib.pyplot as plt
import gurobipy as gp
from gurobipy import GRB
import pulp

def solve_milp(model, solver_name='gurobi', filename='solution.csv', mps = False):
    """
    Solves a given MILP model using the specified solver, saves the solution and bounds to a CSV file.
    
    Parameters:
        model (pyo.Model): The PMS or Pyomo model to be solved.
        solver_name (str): The solver to use ('gurobi', 'glpk', 'cbc') or a custom solver.
        filename (str): The name of the CSV file where the solution will be saved.
        mps (bool): True if model is an MPS file, false if model is a Pyomo model
        
    
    Returns:
        str: Solver status and saves the solution in a CSV file.
    """
    if not mps:
        # Create a solver
        if solver_name == 'gurobi':
            solver = pyo.SolverFactory('gurobi')
        elif solver_name == 'cbc':
            solver = pyo.SolverFactory('cbc')
        else:
            solver = pyo.SolverFactory('glpk')
        
        # Solve the model
        result = solver.solve(model, tee=True)  # 'tee=True' prints solver output

        # Prepare data to save
        data = []
        for v in model.component_objects(pyo.Var, active=True):
            varobject = getattr(model, str(v))
            for index in varobject:
                data.append([str(v), index, varobject[index].value])

        # Adding bounds to the data if available
        if hasattr(result.problem, 'upper_bound') and hasattr(result.problem, 'lower_bound'):
            data.append(['Primal Bound', '', result.problem.upper_bound])
            data.append(['Dual Bound', '', result.problem.lower_bound])
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(data, columns=['Variable', 'Index', 'Value'])
        df.to_csv(filename, index=False)
        
        # Check solver status
        if result.solver.status == pyo.SolverStatus.ok:
            if result.solver.termination_condition == pyo.TerminationCondition.optimal:
                return 'Optimal solution found and saved!'
            elif result.solver.termination_condition == pyo.TerminationCondition.infeasible:
                return 'Model is infeasible!'
            else:
                return 'Solution found and saved with status: ' + str(result.solver.status)
        else:
            return 'Solver status: ' + str(result.solver.status)
    else:
        try:
            # Load the MPS file into an LpProblem object
            model = pulp.LpProblem.fromMPS(filename)[1]


            # Select the solver based on the input
            if solver_name == 'gurobi':
                solver = pulp.GUROBI_CMD(msg=True)
            elif solver_name == 'glpk':
                solver = pulp.GLPK_CMD(msg=True)
            else:
                solver = pulp.PULP_CBC_CMD(msg=True)

            # Solve the model using the chosen solver
            model.solve(solver)

            # Print the status of the solution
            print("Status:", pulp.LpStatus[model.status])

            # Print the values of the variables
            for v in model.variables():
                print(f"{v.name} = {v.varValue}")

            # Optionally, print the objective value
            print("Objective Value:", pulp.value(model.objective))

        except Exception as e:
            print("An error occurred:", str(e))


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

# Solve the model
#solve_status = solve_milp(model, 'gurobi', 'gurobi_example_solution.csv')
#solve_status = solve_milp(model, 'glpk', 'glpk_example_solution.csv')
#solve_status = solve_milp(model, 'cbc', 'cbc_example_solution.csv')
#solve_status = solve_milp('/Users/xanderbackus/example_model.mps', 'gurobi', 'gurobi_mps_example_solution.csv',True)
#solve_status = solve_milp('/Users/xanderbackus/instances/1_item_placement/train/item_placement_0.mps', 'gurobi', 'gurobi_mps_example_solution2.csv',True)
#solve_status = solve_milp('/Users/xanderbackus/unit_commitment.mps', 'gurobi', 'gurobi_mps_example_solution3.csv',True)