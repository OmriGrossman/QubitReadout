"""
This module contains utility functions for simulations and calculations.
"""

import numpy as np


def simulate_iq_response(state, amplitude, frequency, noise_level=0.5):
    """Simulate IQ response for a qubit state with noise and frequency shift."""
    response = np.array([1.0, 0.0]) if state == "0" else np.array([-1.0, 0.0])
    response *= amplitude
    response += np.array([np.cos(2 * np.pi * frequency), np.sin(2 * np.pi * frequency)]) * 0.1  # Frequency shift
    response += np.random.normal(0, noise_level, response.shape)
    return response


def calculate_fidelity(iq_data_0, iq_data_1):
    """Compute the readout fidelity."""
    mean_0 = np.mean(iq_data_0, axis=0)
    mean_1 = np.mean(iq_data_1, axis=0)

    correct_0 = sum(np.linalg.norm(p - mean_0) < np.linalg.norm(p - mean_1) for p in iq_data_0)
    correct_1 = sum(np.linalg.norm(p - mean_1) < np.linalg.norm(p - mean_0) for p in iq_data_1)

    return (correct_0 + correct_1) / (len(iq_data_0) + len(iq_data_1))
