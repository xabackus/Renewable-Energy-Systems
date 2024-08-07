import pandas as pd
import pyomo.environ as pyo

def solve_milp(model, solver_name='gurobi', filename='solution.csv', type = 'mps'):
    """
    Solves a given MILP model using the specified solver, saves the solution and bounds to a CSV file.
    
    Parameters:
        model (pyo.Model): The PMS or Pyomo model to be solved.
        solver_name (str): The solver to use ('gurobi', 'glpk', 'cbc') or a custom solver.
        filename (str): The name of the CSV file where the solution will be saved.
        type (str): pyomo if model is a pyomo model, or mps if model is an address to an mps model
        
    
    Returns:
        str: Solver status and saves the solution in a CSV file.
    """
    if type.lower() == 'pyomo':
        # Create a solver
        if solver_name == 'gurobi':
            solver = pyo.SolverFactory('gurobi')
        elif solver_name == 'cbc':
            solver = pyo.SolverFactory('cbc')
        elif solver_name=='glpk':
            solver = pyo.SolverFactory('glpk')
        else:
            print('solver not supported yet, please update code or contact Xander')
        
        # Solve the model
        result = solver.solve(model, tee=True)  # 'tee=True' prints solver output

        # Prepare data to save
        data = []
        for v in model.component_objects(pyo.Var, active=True):
            varobject = getattr(model, str(v))
            for index in varobject:
                data.append([str(v), index, varobject[index].value])

        # Adding bounds to the data if available
        if hasattr(result.problem, 'upper_bound') and hasattr(result.problem, 'lower_bound'):
            data.append(['Primal Bound', '', result.problem.upper_bound])
            data.append(['Dual Bound', '', result.problem.lower_bound])
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(data, columns=['Variable', 'Index', 'Value'])
        df.to_csv(filename, index=False)
        
        # Check solver status
        if result.solver.status == pyo.SolverStatus.ok:
            if result.solver.termination_condition == pyo.TerminationCondition.optimal:
                return 'Optimal solution found and saved!'
            elif result.solver.termination_condition == pyo.TerminationCondition.infeasible:
                return 'Model is infeasible!'
            else:
                return 'Solution found and saved with status: ' + str(result.solver.status)
        else:
            return 'Solver status: ' + str(result.solver.status)
    elif type.lower() == 'mps':
        import gurobipy as gp
        from gurobipy import GRB
        import csv
        
        try:
            # Read the model
            m = gp.read(model)
            m.setParam('OutputFlag', True)  # Enable solver output
            m.optimize()
            
            # Check if the model has an optimal solution
            if m.status == GRB.OPTIMAL or m.status == GRB.SUBOPTIMAL:
                # Save the variables and values to CSV
                with open(filename, 'w', newline='') as csvfile:
                    fieldnames = ['Variable', 'Value']
                    writer = csv.writer(csvfile)
                    writer.writerow(fieldnames)
                    
                    # Writing variables and their solution values
                    for var in m.getVars():
                        writer.writerow([var.varName, var.x])
                    
                    # Appending primal and dual bounds
                    writer.writerow(['Primal Bound', m.ObjVal])
                    if hasattr(m, 'ObjBound'):
                        writer.writerow(['Dual Bound', m.ObjBound])
                    else:
                        writer.writerow(['Dual Bound', 'Not Available'])

                return 'Optimal or suboptimal solution found and saved!'
            elif m.status == GRB.INFEASIBLE:
                return 'Model is infeasible!'
            elif m.status == GRB.UNBOUNDED:
                return 'Model is unbounded!'
            else:
                return 'Solution found and saved with status: ' + str(m.status)
        
        except Exception as e:
            return 'An error occurred: ' + str(e)
    else:
        print('model type not supported yet, please update code or contact Xander')