import mip
from pyomo.environ import *

def convert_mip_to_pyomo(mip_model):
    # Create a new Pyomo model
    pyomo_model = ConcreteModel()

    # Map MIP variables to Pyomo variables
    pyomo_model.vars = Var(range(len(mip_model.vars)), domain=Reals)
    for i, var in enumerate(mip_model.vars):
        pyomo_var = pyomo_model.vars[i]
        pyomo_var.setlb(var.lb)
        pyomo_var.setub(var.ub)
        if var.var_type == mip.INTEGER:
            pyomo_var.domain = Integers

    # Add objective function
    if mip_model.sense == mip.MINIMIZE:
        pyomo_model.objective = Objective(
            expr=sum(var.obj * pyomo_model.vars[i] for i, var in enumerate(mip_model.vars)),
            sense=minimize)
    else:
        pyomo_model.objective = Objective(
            expr=sum(var.obj * pyomo_model.vars[i] for i, var in enumerate(mip_model.vars)),
            sense=maximize)

    # Add constraints
    pyomo_model.constraints = ConstraintList()
    for constr in mip_model.constrs:
        # Access variables and coefficients in the constraint
        lhs_expr = 0
        for term in constr.expr.terms:
            var_index = mip_model.vars.index(term[0])
            coef = term[1]
            lhs_expr += coef * pyomo_model.vars[var_index]
        
        # Determine the sense and right-hand side of the constraint
        if constr.sense == mip.Constraint.Sense.LE:
            pyomo_model.constraints.add(lhs_expr <= constr.rhs)
        elif constr.sense == mip.Constraint.Sense.EQ:
            pyomo_model.constraints.add(lhs_expr == constr.rhs)
        elif constr.sense == mip.Constraint.Sense.GE:
            pyomo_model.constraints.add(lhs_expr >= constr.rhs)

    return pyomo_model

def solve_mps_with_pyomo(mps_file_path, solver_name):
    # Read the MPS file using mip
    mip_model = mip.Model()
    mip_model.read(mps_file_path)

    # Convert to Pyomo model
    pyomo_model = convert_mip_to_pyomo(mip_model)

    # Solve using Pyomo
    solver = SolverFactory(solver_name)
    result = solver.solve(pyomo_model, tee=True)

    # Print results
    print("Status:", result.solver.status)
    print("Termination condition:", result.solver.termination_condition)
    for v in pyomo_model.vars.values():
        print(f"{v}: {v.value()}")

# Example usage:
if __name__ == "__main__":
    solve_mps_with_pyomo('/Users/xanderbackus/instances/1_item_placement/train/item_placement_0.mps', 'cbc')