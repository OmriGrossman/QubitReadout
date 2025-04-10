"""
This module handles hardware configuration and connectivity.
"""

from laboneq.simple import DeviceSetup


def get_device_setup(device_id=None):
    """Get a device setup for the specified device or simulator."""
    if device_id:
        # Set up for real hardware
        return DeviceSetup(device_id)
    else:
        # Set up for simulator
        return DeviceSetup.simulator()


def configure_device(device_setup):
    """Configure the experiment hardware device."""
    device_setup.configure_channel("readout_signal", port=1)
    device_setup.configure_channel("qubit_drive", port=2)
    return device_setup
