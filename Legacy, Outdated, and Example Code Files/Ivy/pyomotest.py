# from pyomo.environ import *

# model = ConcreteModel("my model")
# model.x = Var()
# model.y = Var()
# model.obj = Objective(expr= model.x + model.y)
# model.c1 = Constraint(expr= model.x + model.y >= 5)
# instance = model.create_instance()
# opt = SolverFactory('gurobi')
# results = opt.solve(instance)
# instance.display()

# model.write("pyomotest.mps")

from pyomo.environ import *
# from pyomo.opt import SolverFactory

# Load the model from the .mps file
# model = model_from_mps('path_to_your_file.mps')

# Create a solver
solver = SolverFactory('gurobi') 
results = solver.solve("pyomotest.mps")

# Solve the problem
# results = solver.solve(model)

# Display the results
# results.display()
print(results)


# Create a solver
# solver = SolverFactory('gurobi') 
# results = solver.solve("pyomotest.mps")

# # Solve the problem
# # results = solver.solve(model)

# # Display the results
# # results.display()
# print(results)