import gurobipy as gp

try:
    # Create a new model
    model = gp.Model()

    # Read the MPS file
    model.read('/Users/xanderbackus/instances/1_item_placement/train/item_placement_0.mps')

    # Optimize the model
    model.optimize()

    # Check if the model has been solved to optimality
    if model.Status == gp.GRB.OPTIMAL:
        print("Optimal solution found!")
        # Print the objective value
        print("Objective Value: ", model.ObjVal)
        # Optionally, print variable decisions
        for var in model.getVars():
            print(f'{var.VarName}: {var.X}')
    elif model.Status == gp.GRB.INFEASIBLE:
        print("Model is infeasible.")
    elif model.Status == gp.GRB.UNBOUNDED:
        print("Model is unbounded.")
    else:
        print("Optimization ended with status ", model.Status)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except Exception as e:
    print('Error during optimization: ', str(e))