import argparse
import numpy as np
import matplotlib.pyplot as plt
from experiment import Experiment
from data_handler import save_results
from error_handling import handle_error
from config import AMPLITUDE_SCALING, FREQUENCY_SCALING, PULSE_SHAPES


def plot_iq_results(results, mode, sweep_param):
    """Plots IQ results for both single and range modes."""
    pulse_shapes = sorted(set(res["pulse_type"] for res in results))
    param_values = sorted(set(res[sweep_param] for res in results))

    num_rows, num_cols = len(pulse_shapes), len(param_values)
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, num_rows * 3), squeeze=False)

    for row_idx, pulse in enumerate(pulse_shapes):
        for col_idx, param in enumerate(param_values):
            result = next(res for res in results if res["pulse_type"] == pulse and res[sweep_param] == param)
            iq_data_0, iq_data_1 = np.array(result["iq_data_0"]), np.array(result["iq_data_1"])

            ax = axes[row_idx, col_idx]
            ax.scatter(iq_data_0[:, 0], iq_data_0[:, 1], color="blue", alpha=0.5, label="|0⟩")
            ax.scatter(iq_data_1[:, 0], iq_data_1[:, 1], color="red", alpha=0.5, label="|1⟩")
            ax.set_title(f"{pulse}, {sweep_param.capitalize()}={param:.2f}\nFidelity: {result['fidelity']:.3f}")
            ax.set_xlabel("I")
            ax.set_ylabel("Q")
            ax.legend()
            ax.grid()

    plt.suptitle(f"IQ Response for Pulse Shapes & {sweep_param.capitalize()} Sweep")
    plt.tight_layout()
    plt.show()


def run_experiment(mode, manual_mode, pulse, amplitude, frequency, sweep_param, save_data, save_format, opt_steps=5):
    """Runs the experiment using ReadoutExperiment class."""
    try:
        if mode == "automatic":  # The program automatically optimizes the best parameters

            from optimization import basic_optimization
            pulse_shapes = PULSE_SHAPES if pulse == "all" else [pulse]

            amp_range = (amplitude * (1 - AMPLITUDE_SCALING), amplitude * (1 + AMPLITUDE_SCALING))
            freq_range = (frequency * (1 - FREQUENCY_SCALING), frequency * (1 + FREQUENCY_SCALING))

            # Call the optimization function
            results = basic_optimization(pulse_shapes, amp_range, freq_range, opt_steps)

            # Display results
            beta_str = f", Beta={results['beta']:.3f}" if results["pulse_type"] == "DRAG" else ""
            print(f"Best parameters are: {results['pulse_type']} pulse, "
                  f"Amplitude={results['amplitude']:.3f}, "
                  f"Frequency={results['frequency']:.3f}{beta_str}, "
                  f"Fidelity={results['fidelity']:.3f}")

            if save_data:
                save_results(results, save_format)

        elif mode == "manual":  # The program outputs the experiment results for manual analysis and optimization
            experiment = Experiment()
            results = []
            pulse_shapes = PULSE_SHAPES if pulse == "all" else [pulse]

            if manual_mode == "single":  # Run a single experiment
                for pulse_type in pulse_shapes:
                    results.append(experiment.run(pulse_type, amplitude, frequency))
            elif manual_mode == "range":  # Sweep over the selected parameter
                amplitude_values = np.linspace(*amplitude, 4) if sweep_param == "amplitude" else [amplitude]
                frequency_values = np.linspace(*frequency, 4) if sweep_param == "frequency" else [frequency]

                for pulse_type in pulse_shapes:
                    for amp in amplitude_values:
                        for freq in frequency_values:
                            results.append(experiment.run(pulse_type, amp, freq))

            plot_iq_results(results, manual_mode, sweep_param)

            if save_data:
                save_results(results, save_format)

    except Exception as e:
        handle_error("Experiment execution failed", e, exit_program=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a qubit readout experiment.")

    # Handle main mode selection
    parser.add_argument("--mode", choices=["automatic", "manual"], required=True,
                        help="Choose between automatic optimization or manual experiment mode.")
    # Handle manual sub-mode selection (only relevant when --mode manual is selected)
    parser.add_argument("--manual_mode", choices=["single", "range"],
                        help="Select 'single' for a single experiment or 'range' for parameter sweeps (manual mode only).")
    # Handle pulse shape selection
    parser.add_argument("--pulse", choices=PULSE_SHAPES + ["all"], required=True,
                        help="Readout pulse shape ('all' to sweep over all shapes)")
    # Handle parameter selection
    parser.add_argument("--amplitude", nargs="+", type=float, required=True,
                        help="For single mode enter one value. For range mode enter min and max values (e.g., 0.5 2.0)")
    parser.add_argument("--frequency", nargs="+", type=float, required=True,
                        help="For single mode enter one value. For range mode enter min and max values (e.g., 6.4 6.6)")
    # Handle parameter sweep settings (only for Range mode)
    parser.add_argument("--sweep_param", choices=["amplitude", "frequency"], default="amplitude",
                        help="Choose whether columns represent amplitude or frequency variations in range mode.")
    # Handle data saving options
    parser.add_argument("--save", action="store_true",
                        help="Flag to save results")
    parser.add_argument("--format", choices=["json", "csv"], default="json",
                        help="File format for saving results")
    # Handle optimization arguments (Only relevant for Automatic mode)
    parser.add_argument("--opt_steps", type=int, default=5,
                        help="Number of steps per parameter for optimization (only in automatic mode)")

    args = parser.parse_args()

    # Validate input parameters correctness
    if args.mode == "manual":
        if args.manual_mode is None:
            parser.error("Manual mode requires --manual_mode to be specified as 'single' or 'range'.")

        if args.manual_mode == "single":
            if len(args.amplitude) != 1 or len(args.frequency) != 1:
                parser.error("Single mode requires exactly one value for amplitude and frequency.")
            amplitude = args.amplitude[0]
            frequency = args.frequency[0]
        elif args.manual_mode == "range":
            if args.sweep_param == "amplitude":
                if len(args.amplitude) != 2 or len(args.frequency) != 1:
                    parser.error("Amplitude sweep requires two amplitude values (min, max) and one frequency value.")
                amplitude = tuple(args.amplitude)
                frequency = args.frequency[0]
            else:  # frequency sweep
                if len(args.frequency) != 2 or len(args.amplitude) != 1:
                    parser.error("Frequency sweep requires two frequency values (min, max) and one amplitude value.")
                frequency = tuple(args.frequency)
                amplitude = args.amplitude[0]
    elif args.mode == "automatic":
        # Ensure exactly one amplitude and frequency value for automatic mode
        if len(args.amplitude) != 1 or len(args.frequency) != 1:
            parser.error("Automatic mode requires exactly one starting value for amplitude and frequency.")

        if args.opt_steps <= 0:
            parser.error("--opt_steps must be a positive integer.")

        amplitude = args.amplitude[0]
        frequency = args.frequency[0]

    # Run the experiment
    run_experiment(args.mode, args.manual_mode if args.mode == "manual" else None,
                   args.pulse, amplitude, frequency, args.sweep_param, args.save, args.format, args.opt_steps)
