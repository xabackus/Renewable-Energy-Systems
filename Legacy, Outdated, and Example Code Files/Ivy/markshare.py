import gurobipy as gp
# from gurobipy import GRB

m = gp.read("markshare_4_0.mps")
# m = gp.read("item_placement_0.mps")
# m = gp.read("item_placement_9.mps")
# m = gp.read("anonymous_0.mps")
# m = gp.read("load_balancing_0.mps")

m.Params.NodeLimit = 1
m.optimize()
print("primal_bound:", m.ObjVal)
print("dual_bound:", m.ObjBound)
# primal: 5, dual: 0
