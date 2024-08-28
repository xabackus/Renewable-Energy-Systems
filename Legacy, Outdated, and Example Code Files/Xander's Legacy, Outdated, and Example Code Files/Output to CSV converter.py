import pyomo.environ as pyo
import csv

# Example Pyomo model setup (replace this with your actual model)
model = pyo.ConcreteModel()
model.x = pyo.Var(within=pyo.NonNegativeIntegers)
model.obj = pyo.Objective(expr=model.x, sense=pyo.minimize)
model.c1 = pyo.Constraint(expr=model.x >= 10)

# Solve the model (replace solver with the one you are using, e.g., 'gurobi')
solver = pyo.SolverFactory('glpk')
result = solver.solve(model, tee=True)

# Function to extract and write the solution to a CSV file
def write_solution_to_csv(model, filename):
    # Check if the solver has successfully solved the model
    if result.solver.status == pyo.SolverStatus.ok and result.solver.termination_condition == pyo.TerminationCondition.optimal:
        # Open the CSV file for writing
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(['Variable', 'Value'])
            # Write each model variable and its solved value
            for v in model.component_objects(pyo.Var, active=True):
                varobject = getattr(model, str(v))
                for index in varobject:
                    writer.writerow([varobject[index], varobject[index].value])
    else:
        print("No optimal solution found.")

# Call the function to write the solution
write_solution_to_csv(model, 'solution.csv')