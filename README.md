# Peripad 504 Touchpad Handler

This project provides Linux support for the Peripad 504 touchpad, enabling full functionality including button clicks, drag operations, and natural scrolling.

## What This Script Does

The `peripad_handler.py` script:

1. **Detects the Peripad 504 touchpad** on your system
2. **Handles button events** (left, right, and middle clicks)
3. **Enables drag operations** by properly managing button press and release events
4. **Implements natural scrolling** (content moves in the direction of your finger movement)
5. **Creates a virtual input device** that passes all events to the system with appropriate modifications

Specifically, the script:
- Creates a virtual input device that mimics the touchpad
- Grabs exclusive access to the hardware device
- Remaps button events to standard mouse buttons
- Inverts scroll directions for natural scrolling
- Passes all other events (cursor movement) through to the system

## Why It Was Created

The Peripad 504 external touchpad doesn't work properly on Ubuntu out of the box:
- Only movement and scrolling work by default
- Button clicks don't register correctly
- Drag operations don't function
- Default scrolling is in the opposite direction of what many users prefer

This script addresses all these issues while maintaining high performance and responsiveness.

## Startup Service Implementation

The script is set up to run automatically at system startup using systemd:

1. A systemd service file (`peripad.service`) was created in `/etc/systemd/system/`
2. The service runs the script with root privileges
3. It starts after the display manager service
4. It's configured to restart automatically if it fails

## Managing the Service

### Starting the Service

```bash
sudo systemctl start peripad.service
```

### Stopping the Service

```bash
sudo systemctl stop peripad.service
```

### Checking Service Status

```bash
sudo systemctl status peripad.service
```

### Restarting the Service

```bash
sudo systemctl restart peripad.service
```

### Enable Automatic Startup

```bash
sudo systemctl enable peripad.service
```

### Disable Automatic Startup

```bash
sudo systemctl disable peripad.service
```

## Removing the Service Completely

To remove the service entirely:

1. Stop the service:
   ```bash
   sudo systemctl stop peripad.service
   ```

2. Disable the service:
   ```bash
   sudo systemctl disable peripad.service
   ```

3. Remove the service file:
   ```bash
   sudo rm /etc/systemd/system/peripad.service
   ```

4. Reload systemd:
   ```bash
   sudo systemctl daemon-reload
   ```

5. Reset systemd:
   ```bash
   sudo systemctl reset-failed
   ```

## Manual Running

If you want to run the script manually without using the service:

```bash
sudo python3 /path/to/peripad_handler.py
```

Press Ctrl+C to stop the script when running it manually.

## Troubleshooting

If the touchpad isn't detected:
- Make sure it's connected properly
- Run `sudo evtest` to list available input devices
- Check if your device shows up as "USB Mouse Pad USB Mouse Pad Mouse"
- Update the `find_peripad_device()` function in the script if your device has a different name

If button clicks aren't working:
- Check if the device is recognized (see status output)
- Ensure the service is running
- Check system logs with `journalctl -u peripad.service` 