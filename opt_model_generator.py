from pyomo.environ import *

def get_get_type_constraints(model, gen_type):
    # Returns constraints specific to the generation type
    return ConstraintList()

def get_general_constraints(model):
    return ConstraintList()

def get_stochastic_constraints(model, stochastic):
    if not stochastic:
        return ConstraintList()
    return ConstraintList()

def get_cost_objective(model, gen_type=None):
    if not gen_type:
        return sum(sum(model.CF[g] * model.u[g, t] + model.CV[g] * model.p[g, t] + model.CSU[g] * model.y[g, t] + model.CSD[g] * model.z[g, t]for g in model.G)for t in model.T)
    return 0

def get_constraints(model):
    model.logice1 = Constraint(model.G, model.T, rule=logice1)
    model.logice2 = Constraint(model.G, model.T, rule=logice2)
    model.pmaxlim = Constraint(model.G, model.T, rule=pmaxlim) # capacity per unit and_period
    model.pminlim = Constraint(model.G, model.T, rule=pmaxlim) # minimum power output per unit and_period
    model.powerbalance = Constraint(model.T, rule=powerbalance) # load balance per period
    model.reserve = Constraint(model.T, rule=reserve) # spinning reserve per period
    model.rampup = Constraint(model.G, model.T, rule=rampup) # ramping_up limit
    model.rampdown = Constraint(model.G, model.T, rule=rampdown) # ramping_down limit

def logice1(model, g, t):
    return model.y[g, t] + model.z[g, t] <= 1

def logice2(model, g, t):
    if t > 1:
        return model.y[g, t] - model.z[g, t] == model.u[g, t] - model.u[g, t-1]
    return model.y[g, t] - model.z[g, t] == model.u[g, t] - model.U0[g]

def powerbalance(model, t):
    return sum(model.p[g, t] for g in model.G) == model.PD[t]
def reserve(model, t):
    return sum(model.Pmax[g] * model.u[g, t] for g in model.G) >= model.PD[t] + model.RRD[t]
def pminlim(model, g, t):
    return model.Pmin[g] * model.u[g, t] <= model.p[g, t]
def pmaxlim(model, g, t):
    return model.p[g, t] <= model.Pmax[g] * model.u[g, t]

def rampup(model, g, t):
        if t > 1:
            return model.p[g, t] - model.p[g, t-1] <= model.RU[g] * model.u[g, t-1] + model.RSU[g] * model.y[g, t]
        return model.p[g, t] - model.P0[g] <= model.RU[g] * model.U0[g] + model.RSU[g] * model.y[g, t]


def rampdown(model, g, t):
        if t > 1:
            return model.p[g, t-1] - model.p[g, t] <= model.RD[g] * model.u[g, t] + model.RSD[g] * model.z[g, t]
        return model.P0[g] - model.p[g, t] <= model.RD[g] * model.u[g, t] + model.RSD[g] * model.z[g, t]

def init_constants(model):
    model.CF = Param(model.G)
    model.CV = Param(model.G)
    model.CSU = Param(model.G)
    model.CSD = Param(model.G)
    model.Pmax = Param(model.G)
    model.Pmin = Param(model.G)
    model.RU = Param(model.G)
    model.RD = Param(model.G)
    model.P0 = Param(model.G)
    model.U0 = Param(model.G)
    model.RSU = Param(model.G)
    model.RSD = Param(model.G)
    model.RRD = Param(model.T)
    model.PD = Param(model.T)

def opt_model_generator(gen_type=None, system_size=30, time_periods=24, stochastic=True):
    model_name = "UC_" + "_".join([str(gen_type), str(system_size), str(time_periods), str(stochastic)])
    model = AbstractModel(model_name)

    # constants
    model.G = RangeSet(1, system_size)
    model.T = RangeSet(1, time_periods)
    init_constants(model)

    # decision variables
    model.p = Var(model.G, model.T, within = NonNegativeReals)
    model.u = Var(model.G, model.T, within = Binary)
    model.y = Var(model.G, model.T, within = Binary)
    model.z = Var(model.G, model.T, within = Binary)

    # objective
    model.cost = Objective(rule=get_cost_objective)

    # constraints
    get_constraints(model) # delete later
    get_get_type_constraints(model, gen_type)
    get_general_constraints(model)
    get_stochastic_constraints(model, stochastic)
    
    return model


model = opt_model_generator(None, 3, 3) # get abstract model

data = DataPortal()
data.load(filename='parameters.dat') # load data from AMPL file
instance = model.create_instance(data) # generate concrete model from abstract model

primal_opt = SolverFactory('gurobi')
primal_opt.options["NodeLimit"] = 0
results = primal_opt.solve(instance) # solve concrete for one iteration
print("primal bound:", value(instance.cost))
opt = SolverFactory('gurobi')
results = opt.solve(instance) # solve concrete for one iteration
print("optimal value:", value(instance.cost))

# instance.write("opt_model_generator.mps")
# print(results)



