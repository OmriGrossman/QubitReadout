Optimizing qubit readout fidelity using Zurich Instruments' LabOneQ

Setup Instructions:
	1. Set up a virtual environment:
		source venv/bin/activate  # macOS/Linux
		.venv\Scripts\activate      # Windows

	2. Install dependencies:
		pip install -r requirements.txt

*This project requires Python 3.8+.

--------------------------------------
Operational instructions:
	The program has two operation modes - Automated parameter optimization, and Manual Parameter Optimization.
	here are example command line commands for running each mode:

	1. Automated Optimization Mode (The program automatically finds the optimal parameters for the readout):
		python main.py --mode automatic --pulse all --amplitude 1.5 --frequency 6.5 --opt_steps 10 --save --format csv

	2. Manual Optimization Mode (Allows the user to choose parameters and analyze the results manually).
	This mode has two options:

		1. Single parameter - Choose a single set of parameters for the experiment. example running command:
			python main.py --mode manual --manual_mode single --pulse Square --amplitude 1.5 --frequency 6.5 --save --format json

		2. Range of parameters - Choose a certain parameter to sweep over and compare the results.
			python main.py --mode manual --manual_mode range --pulse all --amplitude 1.5 --frequency 6.4 6.6 --sweep_param frequency --save --format csv

* In Manual Range Mode you need to choose which parameter you want to sweep over:
	--sweep_param amplitude: Sweeps over amplitude with fixed frequency.
	--sweep_param frequency: Sweeps over frequency with fixed amplitude.
* Results are saved in the /experiment_results/ folder.
* The program supports JSON/CSV data output formats.

Get help:
	To see all available options, modes and variables use:
		python main.py --help
