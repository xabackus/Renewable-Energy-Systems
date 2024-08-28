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

def init_constants(model, gen_type, stochastic):
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
    init_constants(model, gen_type, stochastic)

    # decision variables
    model.p = Var(model.G, model.T, within = NonNegativeReals)
    model.u = Var(model.G, model.T, within = Binary)
    model.y = Var(model.G, model.T, within = Binary)
    model.z = Var(model.G, model.T, within = Binary)

    # objective
    model.cost = Objective(rule=get_cost_objective)

    # constraints
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
