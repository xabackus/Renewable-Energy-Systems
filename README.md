# Renewable Energy Systems

## Description
This project focuses on modeling renewable energy systems using Mixed-Integer Linear Programming (MILP) techniques. It provides tools to generate optimization models and solve them using various solvers. The project aims to facilitate the analysis and optimization of renewable energy systems through robust computational models.

## Files
- **`main.py`**: The main driver script for the project. This file orchestrates the data collection, model creation, and optimization processes.
  
- **`solver.py`**: Contains the core functions for setting up and solving the MILP models. This script interfaces with Gurobi and handles the solution process, including the application of various Gurobi settings to optimize the solution gap.

- **`helpers.py`**: Includes utility functions that support the main operations, such as data processing, handling inputs and outputs, and managing intermediate calculations.

- **`example.py`**: A sample script demonstrating how to use the provided tools and models. This file is designed to help users understand the basic workflow of the project.

- **`model.pdf`**: Documentation of the unit commitment model used in this project. This document provides an in-depth explanation of the sets, parameters, variables, objective function, and constraints used in the MILP formulation.

- **`settings.py`**: Illustrates the effect on the solution gap of changing each of Gurobi's cut settings. While the actual effect of changing a given setting depends on your precise unit commitment problem, it is always the same settings that have some effect, since they are the settings used in solving UC problems. Thus, this table is useful for getting an idea of what settings you should experiment on changing.

## Installation
To get started with this project, follow these steps:

`git clone https://github.com/xabackus/Renewable-Energy-Systems.git`
`cd Renewable-Energy-Systems`

Ensure you have Python installed, and then install the necessary dependencies:

`pip install pyomo gurobipy matplotlib pandas numpy`

## Usage
### Generating and Solving Models
To generate and solve an optimization model:
1. Run the command
`example.py [num_solar] [num_wind] [num_hydro] [num_batt] [num_therm]`
Currently, the model generator only supports the standard IEEE 30-bus system with 5 thermal generators and can add any number of solar, wind and battery generators on top of it.
2. The model and data will be saved into the "UCmodel.mps" and "UCdata.p" files.
3. Edit `solver.py` to solve the model with your preferred solver (after editing, run the solver with `python solver.py`). If you want to change Gurobi's cut settings, you can do it here.

Example usage is detailed within the scripts, guiding you on setting up your parameters and selecting the solver.

## Contributing
We welcome contributions to this project! If you have access to real-world datasets on renewable energy systems that can be modeled as MILPs, or if you have suggestions for improving the model or code, please feel free to contribute. Follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License
This project is released under the MIT License. See the LICENSE file for more details.

## Gurobi License
Gurobi requires a comercial or academic license if you wish to use it to solve large problems. If you wish to use GLPK in `Choose_your_solver.py` for free to solve Pyomo models, you can do so, but Gurobi is the only solver for MPS models currently supported in this script, so if you intend to use this script to solve large problems from MPS files, you will require a paid Gurobi license, and solving even small problems using Gurobi will require that a free license be downloaded from the web.

## Contact
For support or inquiries, contact me at xabackus@mit.edu
