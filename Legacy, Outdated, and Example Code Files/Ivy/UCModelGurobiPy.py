import gurobipy as gp

G = [1, 2, 3]
T = [1, 2, 3]
Pmin = [0, 50, 80, 40]
Pmax = [0, 350, 200, 140]
RD = [0, 300, 150, 100]
RSD = [0, 300, 150, 100]
RU = [0, 200, 100, 100]
RSU = [0, 200, 100, 100]
CF = [0, 5, 7, 6]
CSU = [0, 20, 18, 5]
CSD = [0, 0.5, 0.3, 1.0]
CV = [0, 0.100, 0.125, 0.150]
PD = [0, 160, 500, 400]
RRD = [0, 16, 50, 40]

U0 = [0, 0, 0, 1]
P0 = [0, 0, 0, 100]

m = gp.Model("Unit Commitment Model")

# NG = 3
# NT = 3

p = m.addVars(G, T, name="p", lb=0)
u = m.addVars(G, T, vtype='B',name="u")
y = m.addVars(G, T, vtype='B',name="y")
z = m.addVars(G, T, vtype='B',name="z")
m.setObjective(sum(sum(CF[g] * u[g, t] + CV[g] * p[g, t] + CSU[g] * y[g, t] + CSD[g] * z[g, t]for g in G)for t in T), gp.GRB.MINIMIZE)

for t in T:
    m.addConstr(sum(p[g, t] for g in G) == PD[t])
    m.addConstr(sum(Pmax[g] * u[g, t] for g in G) >= PD[t] + RRD[t])
    for g in G:
        m.addConstr(y[g, t] + z[g, t] <= 1)
        m.addConstr(Pmin[g] * u[g, t] <= p[g, t])
        m.addConstr(p[g, t] <= Pmax[g] * u[g, t])
        if t > 1:
            m.addConstr(y[g, t] - z[g, t] == u[g, t] - u[g, t-1])
            m.addConstr(p[g, t] - p[g, t-1] <= RU[g] * u[g, t-1] + RSU[g] * y[g, t])
            m.addConstr(p[g, t-1] - p[g, t] <= RD[g] * u[g, t] + RSD[g] * z[g, t])
        else:
            m.addConstr(y[g, t] - z[g, t] == u[g, t] - U0[g])
            m.addConstr(p[g, t] - P0[g] <= RU[g] * U0[g] + RSU[g] * y[g, t])
            m.addConstr(P0[g] - p[g, t] <= RD[g] * u[g, t] + RSD[g] * z[g, t])

# m.optimize()

# print(f"Optimal objective value: {m.objVal}")
m.Params.NodeLimit = 1
m.optimize()
print("primal_bound:", m.ObjVal)
print("dual_bound:", m.ObjBound)