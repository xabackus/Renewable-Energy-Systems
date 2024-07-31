# Renewable Energy Systems

## Description
This project focuses on modeling renewable energy systems using Mixed-Integer Linear Programming (MILP) techniques. It provides tools to generate optimization models and solve them using various solvers. The project aims to facilitate the analysis and optimization of renewable energy systems through robust computational models.

## Files
- `opt_model_generator.py`: Generates optimization models for renewable energy systems. It includes functions for defining constraints, objective functions, and the model itself based on given parameters.
- `Choose_your_solver.py`: Allows users to solve the generated models using different MILP solvers like Gurobi, CBC, or GLPK and save the solutions to CSV files.

## Installation
To get started with this project, follow these steps:

`git clone https://github.com/xabackus/Renewable-Energy-Systems.git`
`cd Renewable-Energy-Systems`

Ensure you have Python installed, and then install the necessary dependencies:

`pip install pyomo gurobipy matplotlib pandas numpy`

## Usage
### Generating and Solving Models
To generate and solve an optimization model:
1. Edit parameters in `opt_model_generator.py` to fit the system you are analyzing.
2. Run the model generator script to create a model (`python opt_model_generator.py`).
3. Edit `Choose_your_solver.py` to solve the model with your preferred solver (`python Choose_your_solver.py`).

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

## Contact
For support or inquiries, contact me at xabackus@mit.edu
