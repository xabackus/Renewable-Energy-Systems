import gurobipy as gp

# Load the MPS file
def load_mps_file(mps_file_path):
    try:
        # Create a new model
        grb_model = gp.read(mps_file_path)
        return grb_model
    except gp.GurobiError as e:
        print("Error loading model:", e)

from pyomo.environ import ConcreteModel, Var, Objective, Constraint, ConstraintList, Reals, maximize, minimize, SolverFactory, value

def gurobi_to_pyomo(grb_model):
    # Create a new Pyomo model
    pyo_model = ConcreteModel()

    # Add variables
    pyo_model.vars = Var([v.VarName for v in grb_model.getVars()], domain=Reals)
    
    # Objective function
    obj_coeffs = {v.VarName: v.Obj for v in grb_model.getVars()}
    if grb_model.ModelSense == -1:  # Maximize
        pyo_model.obj = Objective(expr=sum(obj_coeffs[v.VarName] * pyo_model.vars[v.VarName] for v in grb_model.getVars()), sense=maximize)
    else:  # Minimize
        pyo_model.obj = Objective(expr=sum(obj_coeffs[v.VarName] * pyo_model.vars[v.VarName] for v in grb_model.getVars()), sense=minimize)

    # Constraints
    pyo_model.constraints = ConstraintList()
    for constr in grb_model.getConstrs():
        lhs_expr = sum(grb_model.getCoeff(constr, var) * pyo_model.vars[var.VarName] for var in grb_model.getVars())
        if constr.Sense == '<':
            pyo_model.constraints.add(lhs_expr <= constr.RHS)
        elif constr.Sense == '>':
            pyo_model.constraints.add(lhs_expr >= constr.RHS)
        else:  # Equality
            pyo_model.constraints.add(lhs_expr == constr.RHS)

    return pyo_model

def solve_with_pyomo(pyo_model):
    # Solve the model using CBC solver
    solver = SolverFactory('gurobi')
    result = solver.solve(pyo_model, tee=True)  # tee=True for verbose output

    # Display results
    print("Solver Status:", result.solver.status)
    print("Solver Termination Condition:", result.solver.termination_condition)
    if result.solver.status == 'ok' and result.solver.termination_condition == 'optimal':
        # Display solution
        for v in pyo_model.vars:
            print(f"{v}: {value(pyo_model.vars[v])}")
    else:
        print("No optimal solution found.")

mps_file_path = '/Users/xanderbackus/example_model.mps'
grb_model = load_mps_file(mps_file_path)
pyo_model = gurobi_to_pyomo(grb_model)
print(pyo_model)
#solve_with_pyomo(pyo_model)