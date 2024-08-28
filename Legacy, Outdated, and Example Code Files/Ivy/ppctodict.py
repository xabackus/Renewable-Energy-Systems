import case4gs
import pickle

ppc = case4gs.case4gs()

def parsecase(num_solar=0, num_wind=0, num_batt=0, num_hydro=0, num_therm=0, time_periods = 24, num_scenarios = 1, \
                        num_nodes = 0, num_lines = 0, num_uncert = 0, num_demands = 0):
    p = {}

    solar_start = 1
    wind_start = solar_start + num_solar
    batt_start = wind_start + num_wind
    hydro_start = batt_start + num_batt
    therm_start = hydro_start + num_hydro
    num_gen = num_solar + num_wind + num_batt + num_hydro + num_therm

    k = .5 # calibrate

    p["RU"] = {therm_start + i : ppc["gen"][i][8]/2 for i in range(num_gen)} # 1/2 of Pmax for thermal
    p["RD"] = {therm_start + i : ppc["gen"][i][9]/2 for i in range(num_gen)}
    p["Dd"] = {t : 10 for t in range(1, time_periods + 1)} # Pd = demand for 1 hour
    # nodal demand, Pd, N * T
    p["Fmax"] = {l : 0 for l in range(1, num_lines + 1)} # check that capacity is enough
    # p["PTDF"] = {(n, l) : 10 for n in range(1, num_nodes+1) for l in range(1, num_lines+1)} # calculate from topology, not in constraint, remove
    p["SU"] = {therm_start + i : k * ppc["gen"][i][8]/2 for i in range(num_gen)}
    p["SD"] = {therm_start + i : k * ppc["gen"][i][9]/2 for i in range(num_gen)}
    p["UT"] = {therm_start + i : 6 for i in range(num_gen)} # or 12
    p["DT"] = {therm_start + i : 6 for i in range(num_gen)} # or 12
    p["Rup"] = {t : .05 * ppc["gen"][0][8] for t in range(1, time_periods + 1)} # 5% of demand
    p["Rdn"] = {t : .05 * ppc["gen"][0][9] for t in range(1, time_periods + 1)} # sum Pmax
    p["Lg"] = {(g, i): 1 for g in range(1, num_gen + 1) for i in range(1, num_nodes + 1)} # fix
    p["Ll"] = {(l, n): 1 for l in range(1, num_lines + 1) for n in range(1, num_gen + 1)}
    p["Ld"] = {(d, i): 1 for d in range(1, num_demands + 1) for i in range(1, num_nodes + 1)}
    p["Dl"] = {d : 1 / num_demands for d in range(1, num_demands)} # remove, percentage of system load allocated to d
    
    p["Dt"] = {None: 1}

    p["Pmax"] = {therm_start + i : ppc["gen"][i][8] for i in range(num_gen)}
    p["Pmin"] = {therm_start + i : ppc["gen"][i][9] for i in range(num_gen)}

    p["X"] = {i : ppc["branch"][i - 1][3] for i in range(1, num_lines + 1)}


    # for i in range(num_lines):
    #     p["Ll"][(ppc["branch"][i][0], ppc["branch"][i][1])] = 1

    if "gencost" in ppc:
        p["CSU"] = {therm_start + i : ppc["gencost"][i][1] for i in range(num_gen)}
        p["CSD"] = {therm_start + i : ppc["gencost"][i][2] for i in range(num_gen)}
        p["CF"] = {therm_start + i : ppc["gencost"][i][4] for i in range(num_gen)}
        p["CV"] = {therm_start + i : ppc["gencost"][i][5] for i in range(num_gen)}
    else:
        p["CSU"] = {therm_start + i : 50 for i in range(num_gen)}
        p["CSD"] = {therm_start + i : 50 for i in range(num_gen)}
        p["CF"] = {therm_start + i : 100 for i in range(num_gen)}
        p["CV"] = {therm_start + i : 30 for i in range(num_gen)}

    
    p["Pi"] = {1: 1} # if deterministic

    return pickle.dumps({None: p})