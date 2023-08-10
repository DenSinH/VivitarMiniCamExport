# Extracting data from Vivitar Mini Camera on Windows

- Firstly, we need to install WSL and allow ourselves to read USB ports from WSL.
  To do this, we follow: https://learn.microsoft.com/en-us/windows/wsl/connect-usb
- Install usbipd: https://github.com/dorssel/usbipd-win/releases
- Run commands in WSL:
    ```
    sudo apt install linux-tools-generic hwdata
    sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20
    ```
- View USB devices (in PS on windows):

    ```
    usbipd wsl list
    ```
    
    output:
    ```
    BUSID  VID:PID    DEVICE                                                        STATE
    1-1    046d:c534  USB-invoerapparaat                                            Not attached
    1-2    2770:9120  USB DIGITAL STILL CAMERA                                      Attached - WSL
    1-4    8087:0aa7  Intel(R) Wireless Bluetooth(R)                                Not attached
    1-5    04f2:b5d5  HP TrueVision HD Camera                                       Not attached
    ```

- Find camera bus (`1-2` in example)
- Connect USB device to WSL
    ```
    usbipd wsl attach --busid <busid> --distribution <distro>
    ```
    so in our case: 
    ```
    usbipd wsl attach --busid 1-2 --distribution Ubuntu
    ```
- In WSL / Ubuntu: check USB devices
    ```
    lsusb
    ```
    Should show camera:
    ```
    Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 001 Device 002: ID 2770:9120 NHJ, Ltd Che-ez! Snap / iClick Tiny VGA Digital Camera
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    ```
- In WSL / Ubuntu: install `gphoto2` with apt
- `cd` to folder to output photos (in ppm format)
- Extract all photos
    ```
    sudo gphoto2 --auto-detect -P
    ```
- The photos are extracted in ppm format, we can convert this to png
  (or any other image format you like) using Pillow in Python.
- Delete all photos from the camera
    ```
    sudo gphoto2 --auto-detect -D
    ```