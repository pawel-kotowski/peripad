#!/usr/bin/env python3
"""
Peripad 504 Event Handler
This script reads raw events from the Peripad 504 touchpad
and creates a virtual input device to handle buttons properly while
maintaining native performance for movements.
"""

import os
import sys
import evdev
import time
import signal
from evdev import InputDevice, categorize, ecodes, UInput

# Button mapping
BUTTON_MAP = {272: ecodes.BTN_LEFT, 273: ecodes.BTN_RIGHT, 274: ecodes.BTN_MIDDLE}

# Scroll event codes
SCROLL_VERTICAL = ecodes.REL_WHEEL
SCROLL_HORIZONTAL = ecodes.REL_HWHEEL
HIGH_RES_SCROLL_VERTICAL = 11  # REL_WHEEL_HI_RES
HIGH_RES_SCROLL_HORIZONTAL = 12  # REL_HWHEEL_HI_RES


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


def main():
    """Main function"""
    # Check if running as root
    if os.geteuid() != 0:
        print("This script must be run as root")
        sys.exit(1)

    # Find the device
    device = find_peripad_device()
    if not device:
        print("Peripad device not found")
        sys.exit(1)

    print(f"Found Peripad device: {device.name}")

    # Get device capabilities
    caps = device.capabilities()

    # Setup signal handler for clean exit
    def signal_handler(sig, frame):
        print("\nExiting...")
        try:
            if "ui" in locals():
                ui.close()
            device.ungrab()
        except:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Create a new input device
        ui = UInput.from_device(device, name="Peripad-Virtual")
        print(f"Created virtual device: {ui.name}")

        # We need to grab the device to get exclusive access
        device.grab()

        # Main event loop
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.code in BUTTON_MAP:
                    # Remap button events
                    ui.write(ecodes.EV_KEY, BUTTON_MAP[event.code], event.value)
                    ui.syn()
                    print(
                        f"Button event: {event.code} -> {BUTTON_MAP[event.code]} (value: {event.value})"
                    )
                else:
                    # Pass through other key events
                    ui.write(event.type, event.code, event.value)
                    ui.syn()
            elif event.type == ecodes.EV_REL:
                if event.code in (SCROLL_VERTICAL, HIGH_RES_SCROLL_VERTICAL):
                    # Invert vertical scroll for natural scrolling
                    ui.write(event.type, event.code, -event.value)
                    if event.code == SCROLL_VERTICAL:
                        print(
                            f"Natural scroll: vertical {event.value} -> {-event.value}"
                        )
                elif event.code in (SCROLL_HORIZONTAL, HIGH_RES_SCROLL_HORIZONTAL):
                    # Invert horizontal scroll for natural scrolling
                    ui.write(event.type, event.code, -event.value)
                    if event.code == SCROLL_HORIZONTAL:
                        print(
                            f"Natural scroll: horizontal {event.value} -> {-event.value}"
                        )
                else:
                    # Pass through other relative events (like movement)
                    ui.write(event.type, event.code, event.value)
                ui.syn()
            elif event.type == ecodes.EV_SYN:
                # Synchronization events
                ui.syn()
            else:
                # Pass through all other events
                ui.write(event.type, event.code, event.value)
                ui.syn()

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        if "ui" in locals():
            ui.close()
        try:
            device.ungrab()
        except:
            pass


if __name__ == "__main__":
    main()
