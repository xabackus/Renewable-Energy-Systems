import gurobipy as gp

# Try to read the model from an MPS file
try:
    m = gp.read("/Users/xanderbackus/instances/1_item_placement/train/item_placement_0.mps")
except gp.GurobiError as e:
    print("Error loading model:", e)
    exit()

# Set cut settings
m.setParam('Cuts', 0)  # Moderate cut aggressiveness
# m.setParam('CliqueCuts', 2)  # Enable clique cuts
# m.setParam('CoverCuts', 2)  # Enable cover cuts
# m.setParam('FlowCoverCuts', 2)  # Enable flow cover cuts
# m.setParam('GomoryCuts', 2)  # Enable Gomory fractional cuts
# m.setParam('MIRCuts', 2)  # Enable mixed integer rounding cuts
# m.setParam('SubMIPCuts', 1)  # Enable but less

# Solve the model
m.optimize()

# Check if the solution is optimal
if m.status == gp.GRB.OPTIMAL:
    print("Optimal solution found:")
    # Retrieve and print the objective value
    print("Objective Value:", m.objVal)
    # Retrieve and print variable values
    for v in m.getVars():
        print(f"{v.varName}: {v.x}")
elif m.status == gp.GRB.INF_OR_UNBD:
    print("Model is infeasible or unbounded")
elif m.status == gp.GRB.INFEASIBLE:
    print("Model is infeasible")
elif m.status == gp.GRB.UNBOUNDED:
    print("Model is unbounded")
else:
    print("Optimization ended with status:", m.status)