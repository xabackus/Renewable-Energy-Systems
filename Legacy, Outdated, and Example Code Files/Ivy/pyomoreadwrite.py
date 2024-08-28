from pyomo.environ import *

solver = SolverFactory('gurobi') 
results = solver.solve("markshare_4_0.mps")
results.write()

model = ConcreteModel("my model")
model.x = Var()
model.y = Var()
model.obj = Objective(expr= model.x + model.y)
model.c1 = Constraint(expr= model.x + model.y >= 5)
instance = model.create_instance()
opt = SolverFactory('gurobi')
results = opt.solve(instance)
instance.display()

model.write("pyomotest.mps")



