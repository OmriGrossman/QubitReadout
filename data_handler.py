"""
This module handles data saving and validation.
"""

import json
import csv
import os
from datetime import datetime
import argparse
from error_handling import handle_error
from config import RESULTS_DIR

# Ensuring the results directory exists, otherwise create it
os.makedirs(RESULTS_DIR, exist_ok=True)


def save_results(results, save_format):
    """Saves experiment results in the specified format."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"{RESULTS_DIR}/experiment_results_{timestamp}.{save_format}"

        csv_fields = ["pulse_type", "amplitude", "frequency", "fidelity"]

        # Ensure results is a list (even if a single dictionary is returned)
        if isinstance(results, dict):
            results = [results]

        if save_format == "json":  # Save the data in json format
            with open(results_filename, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {results_filename}")
        elif save_format == "csv":  # Save the data in csv format
            with open(results_filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=csv_fields)
                writer.writeheader()

                for result in results:
                    filtered_result = {key: result[key] for key in csv_fields if key in result}
                    writer.writerow(filtered_result)

            print(f"Results saved to {results_filename}")

        else:
            raise ValueError(f"Unsupported save format: {save_format}")

    except Exception as e:
        handle_error(f"Failed to save results to {results_filename}", e)


def validate_value(value, min_val=None, max_val=None):
    """Ensures a float value is within the specified range."""
    try:
        value = float(value)
        if min_val is not None and value < min_val:
            raise argparse.ArgumentTypeError(f"Value must be at least {min_val}.")
        if max_val is not None and value > max_val:
            raise argparse.ArgumentTypeError(f"Value must be at most {max_val}.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid float value: {value}")
