"""
This module contains automated readout parameter optimizations.
"""

import numpy as np
import sys
from tqdm import tqdm
from experiment import Experiment


def basic_optimization(pulse_types, amplitude_range, frequency_range, steps=5):
    """A basic algorithm for grid-search type optimization."""
    experiment = Experiment()
    best_fidelity = 0
    best_params = None

    amp_values = np.linspace(amplitude_range[0], amplitude_range[1], steps)
    freq_values = np.linspace(frequency_range[0], frequency_range[1], steps)

    # Compute total number of iterations based on the number of values to go over
    total_iterations = sum(len(amp_values) * len(freq_values) * (steps if pulse == "DRAG" else 1) for pulse in pulse_types)

    # Going over all possible parameters to find the best combination for optimal fidelity
    with tqdm(total=total_iterations, desc="Grid Search Progress", file=sys.stdout) as pbar:
        for pulse in pulse_types:
            beta_values = np.linspace(0.1, 1.0, steps) if pulse == "DRAG" else [None]
            for amp in amp_values:
                for freq in freq_values:
                    for beta in beta_values:
                        result = experiment.run(pulse, amp, freq, beta)

                        if result['fidelity'] > best_fidelity:
                            best_fidelity = result['fidelity']
                            best_params = (pulse, amp, freq, beta)

                        pbar.update(1)  # Update progress bar for each parameter combination

    return {
        "pulse_type": best_params[0],
        "amplitude": best_params[1],
        "frequency": best_params[2],
        "beta": best_params[3] if best_params[0] == "DRAG" else None,  # Include beta only for DRAG
        "fidelity": best_fidelity
    }
