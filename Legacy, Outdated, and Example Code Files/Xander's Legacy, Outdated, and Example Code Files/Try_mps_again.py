import pulp

# Load the MPS file
tup = pulp.LpProblem.fromMPS("/Users/xanderbackus/example_model.mps")
print(tup)
model = tup[1]
#print(type(model))
#print(len(model))

#for i in tup:
#    print(i)
#    print(type(i))

# Solve the model using CBC
model.solve(pulp.PULP_CBC_CMD(msg=True))

# Print the status of the solution
print("Status:", pulp.LpStatus[model.status])

# Print the optimal values of the variables
for v in model.variables():
    print(v.name, "=", v.varValue)

# Optionally, print the objective value
print("Objective Value:", pulp.value(model.objective))
