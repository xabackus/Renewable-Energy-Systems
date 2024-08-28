import pandas as pd
from pulp import LpProblem, PULP_CBC_CMD, GLPK_CMD, GUROBI_CMD

def solve_milp(mps_file, solver, csv_output_path):
    # Load the MPS file into an LpProblem
    model = LpProblem.fromMPS(filename=mps_file, sense='MIN')

    #print(model)

    if solver.lower() == 'cbc':
        solver = PULP_CBC_CMD(msg=True)  # CBC solver
    elif solver.lower() == 'glpk':
        solver = GLPK_CMD(msg=True)      # GLPK solver
    elif solver.lower() == 'gurobi':
        solver = GUROBI_CMD(msg=True)    # Gurobi solver
    
    model.solve(solver)

    # Extracting results
    solution_data = [{"Variable": v.name, "Value": v.varValue} for v in model.variables()]

    # Convert to DataFrame
    solution_df = pd.DataFrame(solution_data)

    # Export to CSV
    solution_df.to_csv(csv_output_path, index=False)
    print(f"Solution saved to '{csv_output_path}'.")

# Example usage of a custom solver
class CustomSolver:
    def solve(self, model):
        # Implement the solving process here
        pass

# Usage
#custom_solver = CustomSolver()
solve_milp('/Users/xanderbackus/instances/1_item_placement/train/item_placement_0.mps', 'glpk', '/Users/xanderbackus/gurobi_output.csv')