from pyomo.environ import *

model = ConcreteModel("my model")
model.x = Var(within = NonNegativeReals)
model.y = Var(within = Integers)
model.z = Var(within = Integers)
model.obj = Objective(expr= model.x + model.y + 2 * model.z, sense=minimize)
model.c1 = Constraint(expr= model.x - 3* model.y <= 5)
model.c2 = Constraint(expr= 2*model.x - model.y + 8* model.z >= 17)
model.c3 = Constraint(expr= 3*model.x + 2*model.y + model.z>= 9)

instance = model.create_instance()

opt = SolverFactory('gurobi')
opt.options["NodeLimit"] = 0
results = opt.solve(instance, tee=True)
print(value(instance.obj)) # GETS PRIMAL BOUND

# instance.display()



# m = gp.Model("my model test")

# x = m.addVar(name='x', lb=0)
# y = m.addVar(name='y', vtype='I')
# z = m.addVar(name='z', vtype='I')

# m.setObjective(x + y + 2 * z, gp.GRB.MINIMIZE)
# m.addConstr( x - 3* y <= 5)
# m.addConstr( 2*x - y + 8* z >= 17)
# m.addConstr( 3*x + 2*y + z>= 9)

# # m.Params.NodeLimit = 0
# m.optimize()
# print("primal_bound:", m.ObjVal) # 16.33
# print("dual_bound:", m.ObjBound) # 5.5
# # optimal is 6.333