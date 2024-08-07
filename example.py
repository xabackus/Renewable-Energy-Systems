from pyomo.environ import *
import ppctodict
import pickle
import opt_model_generator as ucml

db = ppctodict.parsecase(num_therm=2, num_nodes=4, num_lines=4, time_periods=3, num_scenarios = 1)
data = pickle.loads(db)
model = ucml.opt_model_generator(num_therm=2, num_nodes=4, num_lines=4, time_periods=3, num_scenarios=1)
model.pprint()

instance = model.create_instance(data)

opt = SolverFactory('gurobi')
result = opt.solve(instance, tee=True)

print("optimal value:", value(instance.cost))
if hasattr(result.problem, 'upper_bound') and hasattr(result.problem, 'lower_bound'):
    primal_bound = result.problem.upper_bound
    dual_bound = result.problem.lower_bound