from pyomo.environ import *

G = [1, 2, 3]
T = [1, 2, 3]
Pmin = [0, 50, 80, 40]
Pmax = [0, 350, 200, 140]
RD = [0, 300, 150, 100]
RSD = [0, 300, 150, 100]
RU = [0, 200, 100, 100]
RSU = [0, 200, 100, 100]
CF = [0, 5, 7, 6]
CSU = [0, 20, 18, 5]
CSD = [0, 0.5, 0.3, 1.0]
CV = [0, 0.100, 0.125, 0.150]
PD = [0, 160, 500, 400]
RRD = [0, 16, 50, 40]

U0 = [0, 0, 0, 1]
P0 = [0, 0, 0, 100]

model = ConcreteModel("Unit Commitment Model")

model.G = Set( initialize=G )
model.T = Set( initialize=T )

model.p = Var(model.G, model.T, within = NonNegativeReals)
model.u = Var(model.G, model.T, within = Binary)
model.y = Var(model.G, model.T, within = Binary)
model.z = Var(model.G, model.T, within = Binary)
model.cost = Objective(expr= sum(sum(CF[g] * model.u[g, t] + CV[g] * model.p[g, t] + CSU[g] * model.y[g, t] + CSD[g] * model.z[g, t]for g in model.G)for t in model.T), sense = minimize)

model.logice = ConstraintList() # start_up shut_down and_running logic
model.pmaxlim = ConstraintList() # capacity per unit and_period
model.pminlim = ConstraintList() # minimum power output per unit and_period
model.powerbalance = ConstraintList() # load balance per period
model.reserve = ConstraintList() # spinning reserve per period
model.rampup = ConstraintList() # ramping_up limit
model.rampdown = ConstraintList() # ramping_down limit

for t in model.T:
    model.powerbalance.add(sum(model.p[g, t] for g in model.G) == PD[t])
    model.reserve.add(sum(Pmax[g] * model.u[g, t] for g in model.G) >= PD[t] + RRD[t])
    for g in model.G:
        model.logice.add(model.y[g, t] + model.z[g, t] <= 1)
        model.pminlim.add(Pmin[g] * model.u[g, t] <= model.p[g, t])
        model.pmaxlim.add(model.p[g, t] <= Pmax[g] * model.u[g, t])
        if t > 1:
            model.logice.add(model.y[g, t] - model.z[g, t] == model.u[g, t] - model.u[g, t-1])
            model.rampup.add(model.p[g, t] - model.p[g, t-1] <= RU[g] * model.u[g, t-1] + RSU[g] * model.y[g, t])
            model.rampdown.add(model.p[g, t-1] - model.p[g, t] <= RD[g] * model.u[g, t] + RSD[g] * model.z[g, t])
        else:
            model.logice.add(model.y[g, t] - model.z[g, t] == model.u[g, t] - U0[g])
            model.rampup.add(model.p[g, t] - P0[g] <= RU[g] * U0[g] + RSU[g] * model.y[g, t])
            model.rampdown.add(P0[g] - model.p[g, t] <= RD[g] * model.u[g, t] + RSD[g] * model.z[g, t])


instance = model.create_instance()
opt = SolverFactory('gurobi')
results = opt.solve(instance)
print(results)
instance.display()

model.write("ucpyomo.mps")