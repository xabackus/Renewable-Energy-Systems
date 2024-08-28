import numpy as np
import matplotlib.pyplot as plt
import pyomo.kernel as pk
import pyomo.environ as pe


def miqp_pk():
    nG, nT = 3, 24
    a, b, c = [0.020, 0.018, 0.025], [2.00, 1.75, 3.00], [0, 0, 0]
    lbpi, ubpi = [30, 20, 15], [80, 60, 40]
    Dt = [83, 75, 70, 66, 66, 70, 77, 87, 97, 105, 115, 123, 131, 138, 145, 151, 156, 159, 158, 153, 144, 136, 123, 107]
    #
    mdl = pk.block()
    mdl.pit = pk.variable_dict({(i, t): pk.variable(lb=0) for i in range(nG) for t in range(nT)})
    mdl.xit = pk.variable_dict({(i, t): pk.variable(domain=pk.Binary) for i in range(nG) for t in range(nT)})
    #
    mdl.obj = pk.objective(
        sense=pk.minimize,
        expr=sum(a[i] * mdl.pit[i, t] ** 2 + b[i] * mdl.pit[i, t] + c[i] for i in range(nG) for t in range(nT)),
    )
    mdl.con1 = pk.constraint_dict({
        t: pk.constraint(expr=sum(mdl.pit[i, t] for i in range(nG)) == Dt[t])  # expr keyword is dispensible
        for t in range(nT)
    })
    mdl.con2a = pk.constraint_dict({
        (i, t): pk.constraint(expr=mdl.pit[i, t] >= mdl.xit[i, t] * lbpi[i])
        for i in range(nG) for t in range(nT)
    })
    mdl.con2b = pk.constraint_dict({
        (i, t): pk.constraint(expr=mdl.pit[i, t] <= mdl.xit[i, t] * ubpi[i])
        for i in range(nG) for t in range(nT)
    })
    mdl.con3 = pk.constraint_dict({
        (i, t): pk.constraint(expr=mdl.xit[i, t] >= mdl.xit[i, t - 1])
        for i in range(nG) for t in range(1, nT)
    })
    #
    rlt = pk.SolverFactory("mosek").solve(mdl)  # use tee=True in solve function if the verbose details are needed
    assert str(rlt.solver.termination_condition) == "optimal"
    pit_ = np.array([[mdl.pit[i, t].value for t in range(nT)] for i in range(nG)])
    return pit_


def miqp_pe():
    nG, nT = 3, 24
    a, b, c = [0.020, 0.018, 0.025], [2.00, 1.75, 3.00], [0, 0, 0]
    lbpi, ubpi = [30, 20, 15], [80, 60, 40]
    Dt = [83, 75, 70, 66, 66, 70, 77, 87, 97, 105, 115, 123, 131, 138, 145, 151, 156, 159, 158, 153, 144, 136, 123, 107]
    #
    mdl = pe.ConcreteModel("MIQP")
    mdl.pit = pe.Var(range(nG), range(nT), bounds=(0, None))
    mdl.xit = pe.Var(range(nG), range(nT), domain=pe.Binary)
    #
    mdl.obj = pe.Objective(
        sense=pe.minimize,
        expr=sum(a[i] * mdl.pit[i, t] ** 2 + b[i] * mdl.pit[i, t] + c[i] for i in range(nG) for t in range(nT)),
    )
    mdl.con1 = pe.ConstraintList()
    for t in range(nT):
        mdl.con1.add(expr=sum(mdl.pit[i, t] for i in range(nG)) == Dt[t])
    mdl.con2a = pe.ConstraintList()
    for i in range(nG):
        for t in range(nT):
            mdl.con2a.add(expr=mdl.pit[i, t] >= mdl.xit[i, t] * lbpi[i])
    mdl.con2b = pe.ConstraintList()
    for i in range(nG):
        for t in range(nT):
            mdl.con2b.add(expr=mdl.pit[i, t] <= mdl.xit[i, t] * ubpi[i])
    mdl.con3 = pe.ConstraintList()
    for i in range(nG):
        for t in range(1, nT):
            mdl.con3.add(expr=mdl.xit[i, t] >= mdl.xit[i, t - 1])
    #
    rlt = pe.SolverFactory("mosek").solve(mdl)
    assert str(rlt.solver.termination_condition) == "optimal"
    pit_ = np.array([[mdl.pit[i, t].value for t in range(nT)] for i in range(nG)])
    return pit_


if __name__ == '__main__':
    plt.figure(1)
    plt.title('PK')
    plt.plot(miqp_pk().transpose())
    #
    plt.figure(2)
    plt.title('PE')
    plt.plot(miqp_pe().transpose())
    #
    plt.show()

