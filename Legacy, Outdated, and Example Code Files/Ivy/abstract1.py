import pyomo.environ as pyo

def create_model():
    model = pyo.AbstractModel()

    model.m = pyo.Param(within=pyo.NonNegativeIntegers)
    model.n = pyo.Param(within=pyo.NonNegativeIntegers)

    model.I = pyo.RangeSet(1, model.m)
    model.J = pyo.RangeSet(1, model.n)

    model.a = pyo.Param(model.I, model.J)
    model.b = pyo.Param(model.I)
    model.c = pyo.Param(model.J)

    # the next line declares a variable indexed by the set J
    model.x = pyo.Var(model.J, domain=pyo.NonNegativeReals)

    def obj_expression(m):
        return pyo.summation(m.c, m.x)

    model.OBJ = pyo.Objective(rule=obj_expression)

    def ax_constraint_rule(m, i):
        # return the expression for the constraint for i
        return sum(m.a[i,j] * m.x[j] for j in m.J) >= m.b[i]

    # the next line creates one constraint for each member of the set model.I
    model.AxbConstraint = pyo.Constraint(model.I, rule=ax_constraint_rule)

model = create_model()
data = pyo.DataPortal()
data.load(filename='opt_model_test.dat')
instance = model.create_instance(data)