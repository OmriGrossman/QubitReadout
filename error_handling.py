"""
This module provides error handling for the entire project.
"""

import sys
import traceback


def handle_error(error_message, exception=None, exit_program=False):
    """
    Handles errors by printing detailed error information.
    """
    full_message = f"Error: {error_message}"

    if exception:
        # Get the traceback information
        tb = traceback.extract_tb(exception.__traceback__)
        # Get the last frame (most recent call)
        last_frame = tb[-1]

        full_message += (
            f"\n  File: {last_frame.filename}"
            f"\n  Line: {last_frame.lineno}"
            f"\n  Error Details: {str(exception)}"
        )

    print(full_message)

    if exit_program:
        sys.exit(1)
