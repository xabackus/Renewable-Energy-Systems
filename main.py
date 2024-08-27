"""Optimization Model Generator"""

from pyomo.environ import *

def get_sets(model, num_solar, num_wind, num_batt, num_hydro, num_therm, time_periods = 24, num_scenarios = 1, \
             num_nodes = 0, num_lines = 0, num_uncert = 0, num_demands = 0):
    """
    G_solar = set of solar generators (first num_solar, from 1)
    G_wind = set of wind generators (next num_wind)
    G_hydro = set of hydro generators (next num_hydro)
    G_batt = set of battery storage units (next num_batt)
    G_therm = set of thermal generators (next G_therm)
    G = set of all generators
    G_renew = set of solar and wind generators (first num_renew generators, from 1)
    T = set of time periods
    S = set of scenarios (0 if deterministic, else indexed 1 to num_scenarios)
    N = set of nodes
    L = set of transmission lines
    O = set of uncertainty realizations (0 if deterministic, else indexed 1 to num_uncert)
    D = set of demands
    """
    num_renew = num_solar + num_wind
    num_gen = num_renew + num_hydro + num_batt + num_therm
    model.Gsolar = RangeSet(1, num_solar)
    model.Gwind = RangeSet(num_solar + 1, num_solar + num_wind)
    model.Ghydro = RangeSet(num_renew + 1, num_renew + num_hydro)
    model.Gbatt = RangeSet(num_renew + num_hydro + 1, num_gen - num_therm)
    model.Gtherm = RangeSet(num_gen - num_therm + 1, num_gen)
    model.G = RangeSet(1, num_gen)
    model.Grenew = RangeSet(1, num_renew)
    model.T = RangeSet(1, time_periods)
    model.T0 = RangeSet(0, time_periods)
    model.S = RangeSet(1, num_scenarios)
    model.N = RangeSet(1, num_nodes)
    model.L = RangeSet(1, num_lines)
    model.O = RangeSet(1, num_uncert)
    model.D = RangeSet(1, num_demands)

def get_parameters(model):
    """
    CF[g] = fixed cost of generator g
    CV[g] = variable cost of generator g
    CSU[g] = start up cost of generator g
    CSD[g] = shut down cost of generator g
    Pi[s] = probability of scenario s
    Pmin[g], Pmax[g] = min and max power output of generator g
    RU[g], RD[g] = ramp up and down rate of generator g
    Dd[t] = demand curve at time t
    Pchg[g] = max charging power for battery g
    Pdchg[g] = max discharging power for battery g
    Hchg[g] = charging efficiency of battery g
    Hdchg[g] = discharging efficiency of battery g
    SoCmin[g], SoCmax[g] = min and max state of charge for battery g
    Fmax[l] = max power flower on line l
    PTDF[n, l] = Power Transfer Distribution Factor for node n and line l
    # Xs[t, o] = realized solar power availability for scenario w and time t
    Xw[t, o] = realized wind power availability for scenario w and time t
    Xd[t, o] = realized electric demand for scenario w and time t
    PXsmax[g, t, o] = max available power from solar generator g based on realized solar availability
    Gam[g] = wind distribution factor for wind generator g
    SU[g], SD[g] = start-up and shut-down rates of generator g
    UT[g], DT[g] = min up and down times of generator g
    Rup[t], Rdn[t] = system-wide up and downward reserve requirements at time t
    L[g, i], L[l, i], L[d, i] = incidence matrices for generators, lines and loads
    X[l] = reactance of line l
    Dl[d] = load distribution factor for demand d
    Dt = time step duration
    Ecap[g] = energy capacity of battery g
    DODmax[g] = max allowable depth of discharge for battery g
    Inflow[g, t, s] = water inflow for hydro generator g at time t in scenario s
    Emin[g], Emax[g] = min and max reservoir levels for hydro generator g
    Qmin[g], Qmax[g] = min and max water discharge for hydro generator g
    Smax[g] = max water spillage for hydro generator g
    Hbase[g] = base head for hydro generator g
    Ebase[g] = base reservoir level for hydro generator g
    A[g], B[g] = initial and final reservoir levels for ghydro generator g
    H[g] = efficiency of hydro generator g
    """
    model.CF = Param(model.G)
    model.CV = Param(model.G)
    model.CSU = Param(model.G)
    model.CSD = Param(model.G)
    model.Pi = Param(model.S)
    model.Pmin = Param(model.G)
    model.Pmax = Param(model.G)
    model.RU = Param(model.G)
    model.RD = Param(model.G)
    model.Dd = Param(model.T)
    model.Pchg = Param(model.Gbatt)
    model.Pdchg = Param(model.Gbatt)
    model.Hchg = Param(model.Gbatt)
    model.Hdchg = Param(model.Gbatt)
    model.SoCmin = Param(model.Gbatt)
    model.SoCmax = Param(model.Gbatt)
    model.Fmax = Param(model.L)
    model.PTDF = Param(model.N, model.L)
    # model.Xs = Param(model.T, model.O)
    model.Xw = Param(model.T, model.O)
    model.Xd = Param(model.T, model.O)
    model.PXsmax = Param(model.Gsolar, model.T, model.O)
    model.Gam = Param(model.Gwind)
    model.SU = Param(model.G)
    model.SD = Param(model.G)
    model.UT = Param(model.G)
    model.DT = Param(model.G)
    model.Rup = Param(model.T)
    model.Rdn = Param(model.T)
    model.Lg = Param(model.G, model.N)
    model.Ll = Param(model.L, model.N)
    model.Ld = Param(model.D, model.N)
    model.X = Param(model.L)
    model.Dl = Param(model.D)
    model.Dt = Param()
    model.Ecap = Param(model.Gbatt)
    model.DODmax = Param(model.Gbatt)
    model.Inflow = Param(model.Ghydro, model.T, model.S)
    model.Emin = Param(model.Ghydro)
    model.Emax = Param(model.Ghydro)
    model.Qmin = Param(model.Ghydro)
    model.Qmax = Param(model.Ghydro)

def get_variables(model):
    """
    u[g, t, s] = iff generator g is on at time t in scenario s (binary)
    y[g, t, s] = iff gneerator g starts up at time t in scenario s (binary)
    z[g, t, s] = iff generator g shuts down at time t in scenario s (binary)
    p[g, t, s] = power output of generator g at time t in scenario s
    r[g, t, s] = reserve provided by generator g at time t in scenario s
    soc[g, t, s] = state of charge for battery g at time t in scenario s
    pchg[g, t, s], pdchg[g, t, s] = charging and discharging power for battery g at time t in scenario s
    uchg[g, t, s], udchg[g, t, s] = charging and discharging of battery g at time t in scenario s (binary)
    ps[g, t, s, o] = second-stage adjustment of generator g at time t in scenario s and realization o
    pmax[g, t, s] = maximum available capacity of generator g at time t in scenario s
    rU[g, t, s], rD[g, t, s] = up and down reserves provided by generator g at time t in scenario s
    uD[d, t, s, o] = unserved demand at bus d at time t in scenario s and realization o
    f[l, t, s, o] = power flow on line l at time t in scenario s and realization o
    th[i, t, s, o] = voltage angle at bus i at time t in scenario s and realization o
    e[g, t, s] = reservoir level of hydro generator g at tiem t in scenario s
    q[g, t, s] = water discharge of hydro generator g at time t in scenario s
    s[g, t, s] = water spillage of hydro generator g at time t in scenario s
    h[g, t, s] = net head of hydro generator g at time t in scenario s 
    """
    model.u = Var(model.G, model.T0, model.S, within = Binary)
    model.y = Var(model.G, model.T, model.S, within = Binary, initialize=0) ###
    model.z = Var(model.G, model.T, model.S, within = Binary, initialize=0) ### 
    model.p = Var(model.G, model.T0, model.S, within = NonNegativeReals)
    model.r = Var(model.G, model.T, model.S, within = NonNegativeReals)
    model.soc = Var(model.Gbatt, model.T0, model.S, within = NonNegativeReals)
    model.pchg = Var(model.Gbatt, model.T, model.S, within = NonNegativeReals)
    model.pdchg = Var(model.Gbatt, model.T, model.S, within = NonNegativeReals)
    model.uchg = Var(model.Gbatt, model.T, model.S, within = Binary)
    model.udchg = Var(model.Gbatt, model.T, model.S, within = Binary)
    model.ps = Var(model.G, model.T0, model.S, model.O, within = NonNegativeReals)
    model.pmax = Var(model.G, model.T, model.S, within = NonNegativeReals)
    model.rU = Var(model.G, model.T, model.S, within = NonNegativeReals)
    model.rD = Var(model.G, model.T, model.S, within = NonNegativeReals)
    model.uD = Var(model.D, model.T, model.S, model.O, within = NonNegativeReals)
    model.f = Var(model.L, model.T, model.S, model.O, within = NonNegativeReals)
    model.th = Var(model.N, model.T, model.S, model.O, within = NonNegativeReals)
    model.e = Var(model.Ghydro, model.T, model.S, within = NonNegativeReals)
    model.q = Var(model.Ghydro, model.T, model.S, within = NonNegativeReals)
    model.s = Var(model.Ghydro, model.T, model.S, within = NonNegativeReals)
    model.h = Var(model.Ghydro, model.T, model.S, within = NonNegativeReals)

def get_objective(model):
    def cost(model):
        return sum(model.Pi[s] * sum(sum(model.CF[g] * model.u[g, t, s] + model.CV[g] * model.p[g, t, s] + \
                    model.CSU[g] * model.y[g, t, s] + model.CSD[g] * model.z[g, t, s]for g in model.G) for t in model.T) for s in model.S)
    model.cost = Objective(rule=cost, sense=minimize)

def get_renewable_constraints(model):
    def solar_limit(model, g, t, s, o):
        return model.p[g, t, s] + model.ps[g, t, s, o] <= model.PXsmax[g, t, o]
    def solar_forecast(model, g, t, s, o):
        return model.p[g, t, s] - model.ps[g, t, s, o] >= 0
    def wind_limit(model, g, t, s, o):
        return model.p[g, t, s] + model.ps[g, t, s, o] <= model.Gam[g] * model.Xw[t, o]
    def wind_forecast(model, g, t, s, o):
        return model.p[g, t, s] - model.ps[g, t, s, o] >= 0
    model.solarlimit = Constraint(model.Gsolar, model.T, model.S, model.O, rule=solar_limit)
    model.solarforecast = Constraint(model.Gsolar, model.T, model.S, model.O, rule=solar_forecast)
    model.windlimit = Constraint(model.Gwind, model.T, model.S, model.O, rule=wind_limit)
    model.windforecast = Constraint(model.Gwind, model.T, model.S, model.O, rule=wind_forecast)

def get_hydro_constraints(model):
    def water_balance(model, g, t, s):
        return model.e[g, t, s] == model.e[g, t-1, s] + model.Inflow[g, t, s] - model.q[g, t, s] - model.s[g, t, s]
    def power_output_hydro(model, g, t ,s):
        return model.p[g, t, s] == model.H[g] * model.q[g, t, s] * model.h[g. t. s]
    def reservoir_min(model, g, t, s):
        return model.Emin[g] <= model.e[g, t, s]
    def reservoir_max(model, g, t, s):
        return model.e[g, t, s] <= model.Emax[g]
    def discharge_min(model, g, t, s):
        return model.Qmin[g] <= model.q[g, t, s]
    def discharge_max(model, g, t, s):
        return model.q[g, t, s] <= model.Qmax[g]
    def spillage_min(model, g, t, s):
        return 0 <= model.s[g, t, s]
    def spillage_max(model, g, t, s):
        return model.s[g, t, s] <= model.Smax[g]
    def head_calculation(model, g, t, s):
        return model.h[g, t, s] == model.Hbase[g] + model.A[g] * (model.e[g, t, s] - model.Ebase[g]) \
            - model.B[g] * model.q[g, t, s] ** 2
    def initial_hydro(model, g, s):
        return model.e[g, 0, s] == model.Einit[g]
    def final_hydro(model, g, s):
        return model.e[g, model.T.dimen, s] == model.Efinal[g]
    model.waterbalance = Constraint(model.Ghydro, model.T, model.S, rule=water_balance)
    model.hydropoweroutput = Constraint(model.Ghydro, model.T, model.S, rule=power_output_hydro)
    model.reservoirmin = Constraint(model.Ghydro, model.T, model.S, rule=reservoir_min)
    model.reservoirmax = Constraint(model.Ghydro, model.T, model.S, rule=reservoir_max)
    model.dischargemin = Constraint(model.Ghydro, model.T, model.S, rule=discharge_min)
    model.dischargemax = Constraint(model.Ghydro, model.T, model.S, rule=discharge_max)
    model.spillagemin = Constraint(model.Ghydro, model.T, model.S, rule=spillage_min)
    model.spillagemax = Constraint(model.Ghydro, model.T, model.S, rule=spillage_max)
    model.headcalculation = Constraint(model.Ghydro, model.T, model.S, rule=head_calculation)
    model.inithydro = Constraint(model.Ghydro, model.S, rule=initial_hydro)
    model.finalhydro = Constraint(model.Ghydro, model.S, rule=final_hydro)

def get_battery_constraints(model):
    def soc_min(model, g, t, s):
        return model.SoCmin[g] <= model.soc[g, t, s]
    def soc_max(model, g, t, s):
        return model.soc[g, t, s] <= model.SoCmax[g]
    def charge_power_min(model, g, t, s):
        return 0 <= model.pchg[g, t, s]
    def charge_power_max(model, g, t, s):
        return model.pchg[g, t, s] <= model.Pchg[g] * model.uchg[g, t, s]
    def discharge_power_min(model, g, t, s):
        return 0 <= model.pdchg[g, t, s]
    def discharge_power_max(model, g, t, s):
        return model.pdchg[g, t, s] <= model.Pdchg[g] * model.udchg[g, t, s]
    def soc_update(model, g, t, s):
        return model.soc[g, t, s] == model.soc[g, t-1, s] + (model.Hchg[g] * model.pchg[g, t, s] - 1/model.Hchg[g] * model.pdchg[g, t, s]) \
            * model.Dt/model.Ecap[g]
    def exclusivity(model, g, t, s):
        return model.uchg[g, t, s] + model.udchg[g, t, s] <= 1
    model.socmin = Constraint(model.Gbatt, model.T, model.S, rule=soc_min)
    model.socmax = Constraint(model.Gbatt, model.T, model.S, rule=soc_max)
    model.chargemin = Constraint(model.Gbatt, model.T, model.S, rule=charge_power_min)
    model.chargemax = Constraint(model.Gbatt, model.T, model.S, rule=charge_power_max)
    model.dischargemin = Constraint(model.Gbatt, model.T, model.S, rule=discharge_power_min)
    model.dischargemax = Constraint(model.Gbatt, model.T, model.S, rule=discharge_power_max)
    model.soc_update = Constraint(model.Gbatt, model.T, model.S, rule=soc_update)
    model.exclusivity = Constraint(model.Gbatt, model.T, model.S, rule=exclusivity)

def get_power_DCPF_constraints(model):
    def nodal_balance(model, t, s, o, i):
        return sum(model.Lg[g, i] * (model.p[g, t, s] + model.ps[g, t, s, o]) for g in model.G) - sum(model.Ll[l, i] * model.f[l, t, s, o] for l in model.L) \
            == sum(model.Ld[d, i] * (model.Dl[d] * model.Xd[t, o] - model.uD[d, t, s, o]) for d in model.D) ###
    def dc_flow(model, l , t, s, o):
        return model.f[l, t, s, o] == sum(model.Ll[l, i] * model.th[i, t, s, o]/model.X[l] for i in model.N)
    def transmission_min(model, l, t, s, o):
        return -model.Fmax[l] <= model.f[l, t, s, o]
    def transmission_max(model, l, t, s, o):
        return model.f[l, t, s, o] <= model.Fmax[l]
    # def system_balance(model, t, s):
    #     return sum(model.p[g, t, s] for g in model.G) + sum((model.pdchg[g, t, s] - model.pchg[g, t, s]) for g in model.Gbatt) == model.Dd[t] ###
    model.nodalbalance = Constraint(model.T, model.S, model.O, model.N, rule=nodal_balance)
    model.dcflow = Constraint(model.L, model.T, model.S, model.O, rule=dc_flow)
    model.transmissionmin = Constraint(model.L, model.T, model.S, model.O, rule=transmission_min)
    model.transmissionmax = Constraint(model.L, model.T, model.S, model.O, rule=transmission_max)
    # model.systembalance = Constraint(model.T, model.S, rule=system_balance)

def get_reserve_constraints(model):
    def reserve_up(model, t, s):
        return sum(model.rU[g, t, s] for g in model.G) >= model.Rup[t]
    def reserve_down(model, t, s):
        return sum(model.rD[g, t, s] for g in model.G) >= model.Rdn[t]
    def reserve_max(model, g, t, s, o):
        return model.p[g, t, s] + model.rU[g, t, s] + model.ps[g, t, s, o] <= model.Pmax[g] # Pmax/min g, t for both?
    def reserve_min(model, g, t, s, o):
        return model.p[g, t, s] - model.rD[g, t, s] - model.ps[g, t, s, o] >= model.Pmin[g] * model.u[g, t, s]
    model.reserve_up = Constraint(model.T, model.S, rule=reserve_up)
    model.reserve_down = Constraint(model.T, model.S, rule=reserve_down)
    model.reserve_max = Constraint(model.G, model.T, model.S, model.O, rule=reserve_max)
    model.reserve_min = Constraint(model.G, model.T, model.S, model.O, rule=reserve_min)

def get_thermal_constraints(model):
    def up_limit(model, g, t, s, o):
        return model.p[g, t, s] + model.ps[g, t, s, o] - (model.p[g, t-1, s] - model.ps[g, t-1, s, o]) \
            <= model.RU[g] * (model.u[g, t, s] - model.y[g, t, s]) + model.SU[g] * model.y[g, t, s]
    def down_limit(model, g, t, s, o):
        if t == len(model.T):
            return Constraint.Skip
        return model.p[g, t, s] + model.ps[g, t, s, o] - (model.p[g, t+1, s] - model.ps[g, t+1, s, o]) \
            <= model.RD[g] * (model.u[g, t, s] - model.z[g, t+1, s]) + model.SD[g] * model.z[g, t+1, s]
    def up_logice(model, g, t, tau, s):
        if t + 1 <= tau <= min(t + model.UT[g] - 1, model.T.dimen):
            return model.y[g, t, s] <= model.u[g, tau, s]
        return Constraint.Skip
    def down_logice(model, g, t, tau, s):
        if t + 1 <= tau <= min(model.T.dimen, t + model.DT[g] - 1):
            return model.z[g, t, s] <= 1 - model.u[g, tau, s]
        return Constraint.Skip
    def logice(model, g, t, s):
        return model.y[g, t, s] - model.z[g, t, s] == model.u[g, t, s] - model.u[g, t-1, s]
    def not_simultaneuous(model, g, t, s):
        return model.y[g, t, s] + model.z[g, t, s] <= 1
    def pminlim(model, g, t, s): 
        return model.Pmin[g] * model.u[g, t, s] <= model.p[g, t, s]
    def pmaxlim(model, g, t, s): # error might be here
        return model.p[g, t, s] <= model.Pmax[g] * model.u[g, t, s]
    def rampup(model, g, t, s):
        return model.p[g, t, s] - model.p[g, t-1, s] <= model.RU[g]
    def rampdown(model, g, t, s):
        return model.p[g, t-1, s] - model.p[g, t, s] <= model.RD[g]
    model.uplimit = Constraint(model.Gtherm, model.T, model.S, model.O, rule=up_limit)
    model.downlimit = Constraint(model.Gtherm, model.T, model.S, model.O, rule=down_limit)
    model.uplogice = Constraint(model.Gtherm, model.T, model.T, model.S, rule=up_logice)
    model.downlogice = Constraint(model.Gtherm, model.T, model.T, model.S, rule=down_logice)
    model.logice = Constraint(model.Gtherm, model.T, model.S, rule=logice)
    model.notsimul = Constraint(model.Gtherm, model.T, model.S, rule=not_simultaneuous)
    model.pminlim = Constraint(model.Gtherm, model.T, model.S, rule=pminlim)
    model.pmaxlim = Constraint(model.Gtherm, model.T, model.S, rule=pmaxlim)
    model.rampup = Constraint(model.Gtherm, model.T, model.S, rule=rampup)
    model.rampdown = Constraint(model.Gtherm, model.T, model.S, rule=rampdown)

def opt_model_generator(num_solar=0, num_wind=0, num_batt=0, num_hydro=0, num_therm=0, time_periods = 24, num_scenarios = 1, \
                        num_nodes = 0, num_lines = 0, num_uncert = 1, num_demands = 0):
    model_name = "UC Model"
    model = AbstractModel(model_name)

    # model set-up
    get_sets(model, num_solar, num_wind, num_batt, num_hydro, num_therm, time_periods, num_scenarios, num_nodes, num_lines, num_uncert, num_demands) # sets
    get_parameters(model)
    get_variables(model)

    # objective
    get_objective(model)

    # constraints
    if num_solar or num_wind:
        get_renewable_constraints(model)
    if num_hydro:
        get_hydro_constraints(model)
    if num_batt:
        get_battery_constraints(model)
    get_power_DCPF_constraints(model)    
    get_reserve_constraints(model)
    if num_therm:
        get_thermal_constraints(model)

    return model
