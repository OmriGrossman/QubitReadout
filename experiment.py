"""
This module handles the LabOneQ experiment, actual or simulated.
"""

import numpy as np
from laboneq.simple import Experiment as LabOneQExperiment, pulse_library, Session
from data_handler import validate_value
from config import NUM_MEASUREMENTS, DEFAULT_AMPLITUDE_RANGE
from utility import simulate_iq_response, calculate_fidelity
from error_handling import handle_error


class Experiment:
    """Handles defining and running qubit readout experiments."""

    def __init__(self, experiment_type='readout', device_id=None, device_config=None):
        """Initialize the experiment class."""
        self.experiment_type = experiment_type
        self.device_id, self.device_config = device_id, device_config
        self._setup_pulses()

        if self.device_id:  # In case real hardware is defined
            try:
                from hardware_config import get_device_setup, configure_device
                self.device_setup = configure_device(get_device_setup(device_id))
            except Exception as e:
                handle_error("Hardware Initialization Error: Failed to initialize ReadoutExperiment"
                             , e, exit_program=True)

    def _setup_pulses(self):
        """Set up available readout and qubit control pulses."""
        self.readout_pulses = {
            "Gaussian": pulse_library.gaussian(uid="readout_gaussian", length=1e-6, amplitude=1.0),
            "Square": pulse_library.const(uid="readout_square", length=1e-6, amplitude=1.0),
            "DRAG": pulse_library.drag(uid="readout_drag", length=1e-6, amplitude=1.0, beta=0.5),
        }
        # Qubit state excitation pulse
        self.pi_pulse = pulse_library.gaussian(uid="x180", length=100e-9, amplitude=1.0)

    def _create_experiment(self, pulse_type, amplitude, frequency):
        """Create a LabOneQ experiment for readout testing."""
        if pulse_type not in self.readout_pulses:
            raise ValueError(f"Invalid pulse type '{pulse_type}'. Must be one of {list(self.readout_pulses.keys())}")

        experiment = LabOneQExperiment(uid=f"{pulse_type}_A{amplitude:.2f}_F{frequency:.2f}")
        readout_pulse = self.readout_pulses[pulse_type]
        readout_pulse.amplitude = validate_value(amplitude, *DEFAULT_AMPLITUDE_RANGE)

        # Define the real-time readout sequence
        with experiment.acquire_loop_rt(uid="readout_loop", count=NUM_MEASUREMENTS):
            # Measuring the qubit in its ground state (|0>)
            with experiment.section(uid="ground_state_measurement", alignment="left"):
                experiment.acquire(signal="readout_signal", handle="ground_state_handle", kernel=readout_pulse)
            # Exciting the qubit to |1> state
            with experiment.section(uid="excited_state_preparation", play_after="ground_state_measurement"):
                experiment.play(signal="qubit_drive", pulse=self.pi_pulse)
            # Measuring the qubit in the excited state (|1>)
            with experiment.section(uid="excited_state_measurement", play_after="excited_state_preparation"):
                experiment.acquire(signal="readout_signal", handle="excited_state_handle", kernel=readout_pulse)

        return experiment

    def run(self, pulse_type, amplitude, frequency, beta=None, num_shots=NUM_MEASUREMENTS):
        """Run an experiment with specified parameters."""
        if pulse_type == "DRAG" and beta is not None:
            self.readout_pulses["DRAG"] = pulse_library.drag(uid="readout_drag", length=1e-6, amplitude=amplitude,
                                                             beta=beta)

        experiment = self._create_experiment(pulse_type, amplitude, frequency)

        if self.device_id:  # In case the experiment is set to run on real hardware
            try:
                results = self._execute_on_hardware(experiment)
                iq_data_0, iq_data_1 = results["ground_state_handle"], results["excited_state_handle"]
            except Exception as e:
                handle_error("Hardware Execution Error.", e)
                return None
        else:  # No hardware defined - simulation mode
            try:
                iq_data_0 = np.array([simulate_iq_response("0", amplitude, frequency) for _ in range(num_shots)])
                iq_data_1 = np.array([simulate_iq_response("1", amplitude, frequency) for _ in range(num_shots)])
            except Exception as e:
                handle_error("Simulation Mode Execution Error.", e)
                return None

        return {
            "pulse_type": pulse_type, "amplitude": amplitude, "frequency": frequency, "iq_data_0": iq_data_0.tolist(),
            "iq_data_1": iq_data_1.tolist(), "fidelity": calculate_fidelity(iq_data_0, iq_data_1)
        }

    def _execute_on_hardware(self, experiment):
        """Execute the experiment on real hardware using LabOneQ."""
        session = Session()
        session.connect(device_id=self.device_id) if self.device_id else session.connect_simulator()
        return session.run(experiment)
