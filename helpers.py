"""Helper functions for using generated optimization models"""

import pickle
import random
import pandapower as pp
import networkx as nx

def parsecase(net, num_solar=0, num_wind=0, num_batt=0, num_hydro=0, num_therm=0, time_periods=24, num_scenarios=1,
              num_nodes=0, num_lines=0, num_uncert=1, num_demands=0):
 
    p = {}

    # Initialize generator ID offset
    gen_offset = 1

    # Thermal Generators
    thermal_gens = net.gen[net.gen.type == "Thermal"]
    Gtherm = list(range(gen_offset, gen_offset + len(thermal_gens)))
    gen_offset += len(Gtherm)

    # Hydro Generators
    hydro_gens = net.gen[net.gen.type == "Hydro"]
    Ghydro = list(range(gen_offset, gen_offset + len(hydro_gens)))
    gen_offset += len(Ghydro)

    # Solar Generators
    solar_sgens = net.sgen[net.sgen.type == "PV"]
    Gsolar = list(range(gen_offset, gen_offset + len(solar_sgens)))
    gen_offset += len(Gsolar)

    # Wind Generators
    wind_sgens = net.sgen[net.sgen.type == "WP"]
    Gwind = list(range(gen_offset, gen_offset + len(wind_sgens)))
    gen_offset += len(Gwind)

    # Battery Storage Units
    battery_storage = net.storage[net.storage.type == "BT"]
    Gbatt = list(range(gen_offset, gen_offset + len(battery_storage)))

    # Renewable Generators (Solar + Wind)
    Grenew = Gsolar + Gwind

    # All Generators
    G = Gtherm + Ghydro + Gsolar + Gwind + Gbatt

    T = range(1, time_periods + 1)
    S = range(1, num_scenarios + 1)
    N = range(1, num_nodes + 1)
    L = range(1, num_lines + 1)
    O = range(1, num_uncert + 1)
    D = range(1, num_demands + 1)

    # Assign generator types to thermal generators
    therm_types = ['coal', 'ccgt']
    gen_types = {g: random.choice(therm_types) for g in Gtherm}

    # Fixed costs
    p["CapEx"] = {
        g: random_range(1342.02, 1544.05) if g in Gsolar else
        random_range(1456.49, 1675.74) if g in Gwind else
        random_range(3181.53, 3660.48) if g in Ghydro else
        random_range(800, 1200) if g in Gbatt else
        random_range(3000, 4000) if gen_types[g] == 'coal' else
        random_range(800, 1000)  # For 'ccgt'
        for g in G
    }
    # Variable costs
    p["OpEx"] = {
        g: random_range(0, 5) if g in Gsolar else
        random_range(0, 5) if g in Gwind else
        random_range(2, 5) if g in Ghydro else
        random_range(5, 10) if g in Gbatt else
        random_range(20, 50) if gen_types[g] == 'coal' else
        random_range(15, 30)  # For 'ccgt'
        for g in G
    }

    # Start-up costs 
    p["CSU"] = {
        g: 0 if g in Grenew or g in Gbatt else
        random_range(1.0, 3.0) if g in Ghydro else
        random_range(180, 220) if gen_types[g] == 'coal' else
        random_range(280, 320)  # For 'ccgt'
        for g in G
    }

    # Shut-down costs ($/MW/Stop)
    p["CSD"] = {
        g: 0 if g in Grenew or g in Gbatt else
        random_range(0.5, 1.5) if g in Ghydro else
        random_range(50, 70) if gen_types[g] == 'coal' else
        random_range(80, 100)  # For 'ccgt'
        for g in G
    }

    # Scenario probabilities
    p["Pi"] = {s: 1 / len(S) for s in range(1, num_scenarios + 1)}

    # Generator limits

    p["Pmax"] = {}
    p["Pmin"] = {}
    for g in G:
        if g in Gsolar or g in Gwind:
            sgen_idx = g - len(Gtherm) - len(Ghydro)  # Adjusted index for sgen
            p["Pmax"][g] = solar_sgens.at[sgen_idx - 1, 'max_p_mw'] if g in Gsolar else wind_sgens.at[
                sgen_idx - 1, 'max_p_mw']
            p["Pmin"][g] = solar_sgens.at[sgen_idx - 1, 'min_p_mw'] if g in Gsolar else wind_sgens.at[
                sgen_idx - 1, 'min_p_mw']
        elif g in Gbatt:
            storage_idx = g - len(Gtherm) - len(Ghydro) - len(Gsolar) - len(Gwind) - 1  # Adjusted index for storage
            p["Pmax"][g] = battery_storage.at[storage_idx, 'max_p_mw']
            p["Pmin"][g] = battery_storage.at[storage_idx, 'min_p_mw']
        elif g in Ghydro or g in Gtherm:
            gen_idx = g - 1  # Adjusted for 1-based indexing
            p["Pmax"][g] = net.gen.at[gen_idx, 'max_p_mw']
            p["Pmin"][g] = net.gen.at[gen_idx, 'min_p_mw']

    # Ramp up and down rates
    p["RU"] = {
        g: p["Pmax"][g] if g in Gbatt else
        p["Pmax"][g] if g in Grenew else
        p["Pmax"][g] if g in Ghydro else

        p["Pmax"][g] * 0.6 if gen_types[g] == 'coal' else  # 60% per hour for coal
        p["Pmax"][g] * 3.0 # 300% per hour for CCGT
        for g in G
    }
    p["RD"] = p["RU"].copy()

    # Battery parameters
    if len(Gbatt) > 0:
        p["Pchg"] = {g: random_range(47.5, 52.5) for g in Gbatt}
        p["Pdchg"] = {g: random_range(47.5, 52.5) for g in Gbatt}
        p["Hchg"] = {g: random_range(0.90, 0.95) for g in Gbatt}
        p["Hdchg"] = {g: random_range(0.90, 0.95) for g in Gbatt}
        p["SoCmin"] = {g: random_range(0.10, 0.20) for g in Gbatt}
        p["SoCmax"] = {g: random_range(0.90, 0.95) for g in Gbatt}
        p["Ecap"] = {g: 100 for g in Gbatt}
        p["DODmax"] = {g: random_range(0.80, 0.90) for g in Gbatt}

    # Solar and wind parameters
    if len(Grenew) > 0:
        p["Xs"] = {
            (o, t): random_range(0.16, 0.23) * random_range(4, 6)
            for o in range(1, num_uncert + 1)
            for t in range(1, time_periods + 1)
        }
        p["PXsmax"] = {
            (g, t, o): p["Xs"][o, t] * p["Pmax"][g]
            for g in Gsolar
            for t in range(1, time_periods + 1)
            for o in range(1, num_uncert + 1)
        }
        p["Gam"] = {g: 0.45 for g in Gwind}

    # Hydro parameters
    if len(Ghydro) > 0:
        p["H"] = {g: (9.81 * 1000 * 0.9) / 1e6 for g in Ghydro}
        p["Smax"] = {g: random_range(276.0, 304.5) for g in Ghydro}  
        p["Hbase"] = {g: 110 for g in Ghydro}
        p["Emin"] = {g: 180 for g in Ghydro}
        p["Emax"] = {g: 220 for g in Ghydro}
        p["Ebase"] = {g: 190 for g in Ghydro}
        p["A"] = {g: 0.02 for g in Ghydro}
        p["B"] = {g: 0.009 for g in Ghydro}
        p["Qmin"] = {g: 15 for g in Ghydro}
        p["Qmax"] = {g: 200 for g in Ghydro}
        p["Inflow"] = {(g, t, s): 120 for g in Ghydro for t in range(1, time_periods + 1) for s in
                       range(1, num_scenarios + 1)}

    # Initialize Einit and Efinal for Hydro Generators
    p["Einit"] = {g: random_range(200, 220) for g in Ghydro}  # Example initial reservoir levels
    p["Efinal"] = {g: p["Einit"][g] for g in
                   Ghydro}  # Example final reservoir levels (can be set differently if needed)


    # Demand curve
    p["Xdemand"] = {
        (t, d): random_range(0.8, 1.2) * net.load.at[d - 1, 'p_mw']
        for t in range(1, time_periods + 1)
        for d in range(1, num_demands + 1)
    }

    p["Dd"] = {
        t: sum(p["Xdemand"][t, d] for d in range(1, num_demands + 1))
        for t in range(1, time_periods + 1)
    }


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


    def reserve_requirement(t):
        base_reserve = 0.03 * p["Dd"][t]  # 3% of demand as base reserve
        renewable_capacity = sum(p["Pmax"][g] for g in Grenew)
        additional_reserve = 0.05 * renewable_capacity  # Additional 5% of renewable capacity
        return base_reserve + additional_reserve

    p["Rup"] = {t: reserve_requirement(t) for t in range(1, time_periods + 1)}
    p["Rdn"] = {t: reserve_requirement(t) for t in range(1, time_periods + 1)}



    # Thermal generator parameters here
    p["Fmax"] = {l: 250 for l in range(1, num_lines + 1)}

    p["SU"] = {
        g: random_range(1,12) if gen_types[g] == 'coal' else 
        random_range(1,2)
        for g in Gtherm
    }
    p["SD"] = {
        g: random_range(4,10) if gen_types[g] == 'coal' else  
        random_range(1,2)
        for g in Gtherm
    }
                
    p["UT"] = {g: 6 for g in Gtherm}  # or 12
    p["DT"] = {g: 6 for g in Gtherm}  # or 12

    p["Lg"] = {}
    for g in G:
        if g in Gsolar:
            sgen_idx = g - len(Gtherm) - len(Ghydro) - 1
            if 0 <= sgen_idx < len(solar_sgens):
                bus = solar_sgens.iloc[sgen_idx]['bus'] + 1
            else:
                raise ValueError(f"Invalid solar generator index: {sgen_idx}")
        elif g in Gwind:
            sgen_idx = g - len(Gtherm) - len(Ghydro) - len(Gsolar) - 1
            if 0 <= sgen_idx < len(wind_sgens):
                bus = wind_sgens.iloc[sgen_idx]['bus'] + 1
            else:
                raise ValueError(f"Invalid wind generator index: {sgen_idx}")
        elif g in Ghydro + Gtherm:
            gen_idx = g - 1
            if 0 <= gen_idx < len(net.gen):
                bus = net.gen.iloc[gen_idx]['bus'] + 1
            else:
                raise ValueError(f"Invalid thermal/hydro generator index: {gen_idx}")
        elif g in Gbatt:
            storage_idx = g - len(Gtherm) - len(Ghydro) - len(Gsolar) - len(Gwind) - 1
            if 0 <= storage_idx < len(battery_storage):
                bus = battery_storage.iloc[storage_idx]['bus'] + 1
            else:
                raise ValueError(f"Invalid battery storage index: {storage_idx}")
        else:
            raise ValueError(f"Unknown generator type for index: {g}")

        for n in N:
            p["Lg"][(g, n)] = 1 if n == bus else 0

    p["Ll"] = {}
    for l in L:
        from_bus = net.line.at[l - 1, 'from_bus'] + 1
        to_bus = net.line.at[l - 1, 'to_bus'] + 1
        for n in N:
            if n == from_bus:
                p["Ll"][(l, n)] = 1
            elif n == to_bus:
                p["Ll"][(l, n)] = -1
            else:
                p["Ll"][(l, n)] = 0

    p["Ld"] = {}
    for d in D:
        bus = net.load.at[d - 1, 'bus'] + 1
        for n in N:
            p["Ld"][(d, n)] = 1 if n == bus else 0


    p["Dl"] = {d: 1 / num_demands for d in range(1, num_demands + 1)}
    p["Dt"] = {None: 1}
                
    p["line_from"] = {l: net.line.at[l - 1, 'from_bus'] + 1 for l in range(1, num_lines + 1)}
    p["line_to"] = {l: net.line.at[l - 1, 'to_bus'] + 1 for l in range(1, num_lines + 1)}
    p["X"] = {l: net.line.at[l - 1, 'x_ohm_per_km'] * net.line.at[l - 1, 'length_km'] for l in range(1, num_lines + 1)}

    S_base = 100  # MVA
    V_base = net.bus['vn_kv'].mean() 
    Z_base = (V_base ** 2) / S_base  # Ohms
    # Convert X[l] from Ohms to per unit
    p["X_pu"] = {l: p["X"][l] / Z_base for l in L}

    # Wind and Battery uncertainty
    p["Xw"] = {
        (t, o): 100 * len(Gwind)
        for t in range(1, time_periods + 1)
        for o in range(1, num_uncert + 1)
    }
    p["Xd_uncert"] = {
        (t, o): 100 * len(Gbatt)
        for t in range(1, time_periods + 1)
        for o in range(1, num_uncert + 1)
    }
                
    # Extract Slack Bus ID
    slack_ext_grid = net.ext_grid[net.ext_grid.type == 'slack']
    if slack_ext_grid.empty:
        raise ValueError("No slack bus found in the network.")
    elif len(slack_ext_grid) > 1:
        raise ValueError("Multiple slack buses found in the network.")
    else:
        slack_bus = slack_ext_grid.at[slack_ext_grid.index[0], 'bus'] + 1  # 1-based indexing
        p["slack_bus"] = slack_bus

    # Serialize data
    data = pickle.dumps({None: p})
    with open("UCdata.p", "wb") as f:
        pickle.dump(data, f)

    return data

def random_range(min_val, max_val):
    return min_val + random.random() * (max_val - min_val)

def add_gens_to_case(net, num_solar, num_wind, num_batt, num_hydro, num_thermal):
    """
    Add specified number of generators of various types to a pandapower network in a specified order.

    Parameters:
    - net: pandapower network object
    - num_solar: Number of solar generators to add
    - num_wind: Number of wind generators to add
    - num_batt: Number of battery storage units to add
    - num_hydro: Number of hydro generators to add
    - num_thermal: Number of thermal generators to add

    Returns:
    - Modified pandapower network object with generators added in specific order.
    """
    # Get list of buses
    buses = net.bus.index.tolist()
    net = add_dummy_loads(net)

    # Ensure we have a slack bus
    if 'type' not in net.ext_grid.columns or 'slack' not in net.ext_grid['type'].values:
        if not net.ext_grid.empty:
            net.ext_grid.loc[net.ext_grid.index[0], 'type'] = 'slack'
        else:
            slack_bus = random.choice(buses)
            pp.create_ext_grid(net, slack_bus, vm_pu=1.0, name="Slack")
            net.ext_grid.loc[net.ext_grid.index[-1], 'type'] = 'slack'

    # Assign 'Thermal' type to existing generators without a type
    if 'type' not in net.gen.columns:
        net.gen['type'] = 'Thermal'
    else:
        net.gen.loc[net.gen['type'].isnull(), 'type'] = 'Thermal'

    # Function to add a generator
    def add_generator(gen_type):
        bus = random.choice(buses)
        unique_id = f"{gen_type}_{len(net.sgen) + len(net.gen) + len(net.storage)}"

        if gen_type == "Solar":
            pp.create_sgen(net, bus, min_p_mw=0, max_p_mw=30, p_mw=30, q_mvar=0, name=unique_id, type="PV")
        elif gen_type == "Wind":
            pp.create_sgen(net, bus, min_p_mw=0, max_p_mw=50, p_mw=50, q_mvar=0, name=unique_id, type="WP")
        elif gen_type == "Battery":
            pp.create_storage(net, bus, min_e_mwh=0, max_e_mwh=20, min_p_mw=-80, max_p_mw=80, p_mw=0, q_mvar=0,
                             name=unique_id, type="BT")
        elif gen_type == "Hydro":
            gen_idx = pp.create_gen(net, bus, min_p_mw=10, max_p_mw=100, p_mw=50, vm_pu=1.0, name=unique_id)
            net.gen.at[gen_idx, "type"] = "Hydro"
        elif gen_type == "Thermal":
            gen_idx = pp.create_gen(net, bus, min_p_mw=20, max_p_mw=200, p_mw=100, vm_pu=1.0, name=unique_id)
            net.gen.at[gen_idx, "type"] = "Thermal"

    # Add Thermal generators
    for _ in range(num_thermal):
        add_generator("Thermal")

    # Add Hydro generators
    for _ in range(num_hydro):
        add_generator("Hydro")

    # Add Solar generators
    for _ in range(num_solar):
        add_generator("Solar")

    # Add Wind generators
    for _ in range(num_wind):
        add_generator("Wind")

    # Add Battery generators
    for _ in range(num_batt):
        add_generator("Battery")

    return net


def add_dummy_loads(net, dummy_load_mw=1):
    """
    Add dummy loads to isolated nodes or nodes without loads in the network.

    Parameters:
    net (pandapower.Network): The pandapower network
    dummy_load_mw (float): The power of the dummy load in MW

    Returns:
    pandapower.Network: The updated network with dummy loads added
    """
    # Create a graph of the network
    graph = nx.Graph()
    for _, line in net.line.iterrows():
        graph.add_edge(line['from_bus'], line['to_bus'])

    # Find all connected components
    connected_components = list(nx.connected_components(graph))

    # Find buses with no loads
    buses_with_loads = set(net.load['bus'].values)
    all_buses = set(net.bus.index)
    buses_without_loads = all_buses - buses_with_loads

    # Add dummy loads to isolated buses and buses without loads
    dummy_load_count = 0
    for bus in buses_without_loads:
        # Check if the bus is isolated (in a component by itself)
        if any(len(component) == 1 and bus in component for component in connected_components):
            pp.create_load(net, bus=bus, p_mw=dummy_load_mw, name=f"Dummy Load {dummy_load_count}")
            dummy_load_count += 1
        # Or if it's in a larger component but has no load
        elif bus not in buses_with_loads:
            pp.create_load(net, bus=bus, p_mw=dummy_load_mw, name=f"Dummy Load {dummy_load_count}")
            dummy_load_count += 1

    print(f"Added {dummy_load_count} dummy loads to the network.")
    return net
