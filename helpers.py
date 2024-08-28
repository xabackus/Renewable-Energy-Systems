"""Helper functions for using generated optimization models"""

import pickle
import random
import pandapower as pp

def parsecase(net, num_solar=0, num_wind=0, num_batt=0, num_hydro=0, num_therm=0, time_periods=24, num_scenarios=1, \
              num_nodes=0, num_lines=0, num_uncert=1, num_demands=0, model_name = "UCdata"):
    p = {}

    solar_start = 1
    wind_start = solar_start + num_solar
    batt_start = wind_start + num_wind
    hydro_start = batt_start + num_batt
    therm_start = hydro_start + num_hydro
    num_gen = num_solar + num_wind + num_batt + num_hydro + num_therm

    T = range(1, time_periods + 1)
    S = range(1, num_scenarios + 1)
    N = range(1, num_nodes + 1)
    L = range(1, num_lines + 1)
    O = range(1, num_uncert + 1)
    D = range(1, num_demands + 1)

    num_renew = num_solar + num_wind
    num_gen = num_renew + num_hydro + num_batt + num_therm
    Gsolar = range(1, num_solar + 1)
    Gwind = range(num_solar + 1, num_solar + num_wind + 1)
    Ghydro = range(num_renew + 1, num_renew + num_hydro + 1)
    Gbatt = range(num_renew + num_hydro + 1, num_gen - num_therm + 1)
    Gtherm = range(num_gen - num_therm + 1, num_gen + 1)
    Grenew = range(1, num_renew + 1)
    G = range(1, num_gen + 1)

    # Assign generator types to thermal generators
    therm_types = ['coal', 'ccgt']
    gen_types = {g: random.choice(therm_types) for g in Gtherm}

    # Fixed costs ($/kW)
    p["CapEx"] = {
        g: random_range(1400, 1500) if g in Gsolar else  
        random_range(1500, 1600) if g in Gwind else  
        random_range(2900, 3100) if g in Ghydro else  
        random_range(1700, 1900) if g in Gbatt else  
        random_range(3800, 4200) if gen_types[g] == 'coal' else random_range(1600, 1800)
        for g in G
    }

    # Variable costs ($/MWh)
    p["OpEx"] = {
        g: random_range(19.5, 21.5) if g in Gsolar else
        random_range(28.5, 31.5) if g in Gwind else
        random_range(85.0, 95.0) if g in Ghydro else
        random_range(40.0, 44.0) if g in Gbatt else
        random_range(80.0, 90.0) if gen_types[g] == 'coal' else random_range(36.0, 40.0)
        for g in G
    }

    # Start-up costs ($/MW/Start)
    p["CSU"] = {
        g: 0 if g in Grenew else
        random_range(2.2, 2.5) if g in Ghydro else
        random_range(9.0, 10.0) if g in Gbatt else
        random_range(160.0, 180.0) if gen_types[g] == 'coal' else random_range(78.0, 88.0)
        for g in G
    }

    # Shut-down costs ($/MW/Stop)
    p["CSD"] = {
        g: 0 if g in Grenew else
        random_range(2.2, 2.5) if g in Ghydro else
        random_range(4.5, 5.0) if g in Gbatt else
        random_range(16.0, 18.0) if gen_types[g] == 'coal' else random_range(8.0, 9.0)
        for g in G
    }

    # Scenario probabilities
    p["Pi"] = {s: 1 / len(S) for s in range(1, num_scenarios + 1)}

    # Generator limits

    p["Pmax"] = {
        g: net.sgen.max_p_mw[g - solar_start] if g in Grenew else
        #    net.hydro.max_p_mw[g-hydro_start] if g in Ghydro else
        net.storage.max_p_mw[g - batt_start] if g in Gbatt else
        net.gen.max_p_mw[g - therm_start]
        for g in G
    }

    p["Pmin"] = {
        g: net.sgen.min_p_mw[g - solar_start] if g in Grenew else
        #    net.hydro.min_p_mw[g-hydro_start] if g in Ghydro else
        net.storage.min_p_mw[g - batt_start] if g in Gbatt else
        net.gen.min_p_mw[g - therm_start]
        for g in G
    }

    # Ramp up and down rates (% of rated capacity per minute)
    p["RU"] = {
        g: 0.55 if g in Gsolar else
        0.25 if g in Gwind else
        0.12 if g in Ghydro else
        1.10 if g in Gbatt else
        0.025 if gen_types[g] == 'coal' else 0.055
        for g in G
    }
    p["RD"] = p["RU"]  # {g: p["RU"][g] for g in G}

    # Battery parameters
    if num_batt > 0:
        p["Pchg"] = {g: random_range(47.5, 52.5) for g in Gbatt}
        p["Pdchg"] = {g: random_range(47.5, 52.5) for g in Gbatt}
        p["Hchg"] = {g: random_range(0.90, 0.95) for g in Gbatt}
        p["Hdchg"] = {g: random_range(0.90, 0.95) for g in Gbatt}
        p["SoCmin"] = {g: random_range(0.10, 0.20) for g in Gbatt}
        p["SoCmax"] = {g: random_range(0.90, 0.95) for g in Gbatt}
        p["Ecap"] = {g: random_range(1.92, 2.10) for g in Gbatt}
        p["DODmax"] = {g: random_range(0.80, 0.90) for g in Gbatt}

    # Solar and wind parameters
    if num_solar + num_wind > 0:
        p["Xs"] = {(o, t): random_range(0.16, 0.23) * random_range(4, 6) for o in O for t in T}
        p["PXsmax"] = {(g, t, o): p["Xs"][(o, t)] * p["Pmax"][g] for g in Gsolar for t in T for o in O}
        p["Gam"] = {g: 0.45 for g in Gwind}

    # Hydro parameters
    if num_hydro > 0:
        p["Qmin"] = {g: random_range(16.63, 18.40) for g in Ghydro}
        p["Qmax"] = {g: random_range(190, 210) for g in Ghydro}
        p["A"] = {g: random_range(0.84, 0.92) for g in Ghydro}
        p["B"] = {g: random_range(0.76, 0.84) for g in Ghydro}
        p["H"] = {g: random_range(0.855, 0.945) for g in Ghydro}
        p["Inflow"] = {(g, t, s): random_range(118.75, 131.25) for g in Ghydro for t in T for s in S}
        p["Emax"] = {g: random_range(218.5, 241.5) for g in Ghydro}
        p["Emin"] = {g: random_range(180.5, 199.5) for g in Ghydro}
        p["Smax"] = {g: random_range(276.0, 304.5) for g in Ghydro}
        p["Hbase"] = {g: random_range(95, 105) for g in Ghydro}
        p["Ebase"] = {g: random_range(203.12, 217.88) for g in Ghydro}

    # # Demand curve
    # total_load = net.load['p_mw'].sum()

    # def demand_curve(t):
    #     base_load = total_load
    #     peak_factor = 1.3
    #     off_peak_factor = 0.7
    #     time_of_day = t % 24
    #     variation = random.uniform(0.95, 1.05)  # Introduces a small random variation of ±5%

    #     if 9 <= time_of_day <= 20:  # Peak hours
    #         return base_load * peak_factor * (1 + 0.1 * np.sin(np.pi * time_of_day / 12)) * variation
    #     else:  # Off-peak hours
    #         return base_load * off_peak_factor * (1 + 0.1 * np.sin(np.pi * time_of_day / 12)) * variation

    # p["Dd"] = {t: demand_curve(t) for t in T}

    p["X"] = {l: net.line.x_ohm_per_km[l - 1] for l in L}

    p["Xw"] = {(t, o): 100 * num_wind for t in T for o in O}  ###

    p["Xd"] = {(t, o, d): random_range(0.8, 1.2) * net.load.p_mw[d - 1]
               for t in T for o in O for d in D}
    p["Dd"] = {t: sum(p["Xd"][t, o, d] for d in D for o in O) for t in T}

    # Reserve requirements
    def reserve_requirement(t):
        base_reserve = 0.03 * p["Dd"][t]  # 3% of demand as base reserve
        renewable_capacity = sum(p["Pmax"][g] for g in Grenew)
        additional_reserve = 0.05 * renewable_capacity  # Additional 5% of renewable capacity
        return base_reserve + additional_reserve

    p["Rup"] = {t: reserve_requirement(t) for t in T}
    p["Rdn"] = {t: reserve_requirement(t) for t in T}

    # Thermal generator parameters here
    k = .5  # calibrate # RU/RD 1/2 of Pmax/min for thermal

    p["Fmax"] = {l: 250 for l in L}

    p["SU"] = {g: k * p["Pmax"][g] / 2 for g in Gtherm}  ### k * RU/D
    p["SD"] = {g: k * p["Pmin"][g] / 2 for g in Gtherm}  ###
    p["UT"] = {g: 6 for g in Gtherm}  # or 12
    p["DT"] = {g: 6 for g in Gtherm}  # or 12

    p["Lg"] = {(g, i): 0 for g in G for i in N}
    for g in G:
        p["Lg"][(g, (
            net.sgen.bus[g - solar_start] if g in Grenew else
            net.hydro.bus[g - hydro_start] if g in Ghydro else
            net.storage.bus[g - batt_start] if g in Gbatt else
            net.gen.bus[g - therm_start]
        ) + 1)] = 1
    p["Ll"] = {(l, i): 0 for l in L for i in N}
    for l in L:
        p["Ll"][(l, net.line.from_bus[l - 1] + 1)] = 1
        p["Ll"][(l, net.line.to_bus[l - 1] + 1)] = -1

    p["Ld"] = {(d, i): 0 for d in D for i in N}

    for d in D:
        p["Ld"][(d, net.load.bus[d - 1] + 1)] = 1

    p["Dl"] = {d: 1 / num_demands for d in D}

    p["Dt"] = {None: 1}

    p["X"] = {l: net.line.x_ohm_per_km[l - 1] for l in L}

    data = pickle.dumps({None: p})
    pickle.dump(data, open("data/" + model_name + ".p", "wb"))
    return data

def random_range(min_val, max_val):
    return min_val + random.random() * (max_val - min_val)

def add_gens_to_case(net, num_solar=0, num_wind=0, num_batt=0):
    for _ in range(num_solar):
        bus = pp.get_free_id(net.bus)
        pp.create_bus(net, vn_kv=net.bus.vn_kv.mean())
        pp.create_sgen(net, bus, min_p_mw=0, max_p_mw=30, p_mw=30, q_mvar=0, name="Solar", type="PV")
        pp.create_line(net, from_bus=pp.get_free_id(net.bus) % len(net.bus), to_bus=bus, length_km=5,
                       std_type="N2XS(FL)2Y 1x300 RM/35 64/110 kV")

    for _ in range(num_wind):
        bus = pp.get_free_id(net.bus)
        pp.create_bus(net, vn_kv=net.bus.vn_kv.mean())
        pp.create_sgen(net, bus, min_p_mw=0, max_p_mw=50, p_mw=50, q_mvar=0, name="Wind", type="WP")
        pp.create_line(net, from_bus=pp.get_free_id(net.bus) % len(net.bus), to_bus=bus, length_km=10,
                       std_type="N2XS(FL)2Y 1x300 RM/35 64/110 kV")

    for _ in range(num_batt):
        bus = pp.get_free_id(net.bus)
        pp.create_bus(net, vn_kv=net.bus.vn_kv.mean())
        pp.create_storage(net, bus, min_e_mwh=0, max_e_mwh=20, min_p_mw=0, max_p_mw=80, p_mw=20, q_mvar=0,
                          name="Battery", type="BT")
        pp.create_line(net, from_bus=pp.get_free_id(net.bus) % len(net.bus), to_bus=bus, length_km=5,
                       std_type="N2XS(FL)2Y 1x300 RM/35 64/110 kV")
    