import pyomo.environ as pyo
from helpers import parsecase
import pickle
import main as ucml
import case4gs

ppc = case4gs.case4gs()
db = parsecase(ppc, num_therm=2, num_nodes=4, num_lines=4, time_periods=3, num_scenarios = 1)
data = pickle.loads(db)
model = ucml.opt_model_generator(num_therm=2, num_nodes=4, num_lines=4, time_periods=3, num_scenarios=1)
model.pprint()

# single helper function so that the kwargs are the same

instance = model.create_instance(data)

opt = pyo.SolverFactory('gurobi')
result = opt.solve(instance, tee=True)

if hasattr(result.problem, 'upper_bound') and hasattr(result.problem, 'lower_bound'):
    primal_bound = result.problem.upper_bound
    dual_bound = result.problem.lower_bound
    print("primal bound:", primal_bound)
    print("dual bound:", dual_bound)

print("optimal value:", pyo.value(instance.cost))

out = {"dual_bound": dual_bound, "primal_bound": primal_bound}
# make a file with output json file, with name
