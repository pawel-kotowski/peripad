#!/usr/bin/env python3
"""
Peripad 504 Event Handler
This script reads raw events from the Peripad 504 touchpad
and simulates mouse clicks using xdotool.
"""

import os
import sys
import subprocess
import evdev
from evdev import InputDevice, ecodes

# Device path - update this if needed
DEVICE_PATH = "/dev/input/event18"
XDOTOOL_PATH = "/usr/bin/xdotool"


def find_peripad_device():
    """Find the Peripad device"""
    for path in evdev.list_devices():
        try:
            device = InputDevice(path)
            if "USB Mouse Pad USB Mouse Pad Mouse" in device.name:
                return device
        except Exception as e:
            print(f"Error accessing device {path}: {e}")
    return None


def run_xdotool(command):
    """Run an xdotool command"""
    try:
        # Run xdotool as the real user
        real_user = os.environ.get("SUDO_USER", os.environ.get("USER"))
        cmd = f"sudo -u {real_user} {XDOTOOL_PATH} {command}"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"xdotool error: {e}")
    except Exception as e:
        print(f"Error running xdotool: {e}")


def handle_event(event):
    """Handle input events"""
    # Only process button events
    if event.type == ecodes.EV_KEY:
        if event.code == 272:  # Left button
            if event.value == 1:  # Press
                run_xdotool("mousedown 1")
            else:  # Release
                run_xdotool("mouseup 1")
        elif event.code == 273:  # Right button
            if event.value == 1:  # Press
                run_xdotool("mousedown 3")
            else:  # Release
                run_xdotool("mouseup 3")
        elif event.code == 274:  # Middle button
            if event.value == 1:  # Press
                run_xdotool("mousedown 2")
            else:  # Release
                run_xdotool("mouseup 2")


def main():
    """Main function"""
    # Check if running as root
    if os.geteuid() != 0:
        print("This script must be run as root")
        sys.exit(1)

    # Check if xdotool exists
    if not os.path.exists(XDOTOOL_PATH):
        print(f"Error: xdotool not found at {XDOTOOL_PATH}")
        sys.exit(1)

    # Find the device
    device = find_peripad_device()
    if not device:
        print("Peripad device not found")
        sys.exit(1)

    print(f"Found Peripad device: {device.name}")
    print("Monitoring events... (Press Ctrl+C to exit)")

    try:
        # Note: We are NOT grabbing the device, so events will be processed by both
        # this script and the normal system handlers

        # Read events
        for event in device.read_loop():
            # Only handle button events, system will handle everything else
            if event.type == ecodes.EV_KEY and event.code in (272, 273, 274):
                handle_event(event)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Close device
        device.close()


if __name__ == "__main__":
    main()
