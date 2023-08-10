import os
from typing import Dict
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
import chardet
import easygui


ALLOW_INSTALLATIONS = True
SAVE_EXT = "png"
DELETE_PHOTOS = False


def try_run(command, use_stdout=True, print_output=True, **kwargs):
    if not use_stdout:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        out, err = proc.communicate()
        enc = chardet.detect(out)["encoding"] or "utf-8"
        out = out.decode(enc)

        if print_output:
            print(out)
        if err:
            print(err.decode(enc))

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, command, output=out, stderr=err.decode(enc))

        return out
    else:
        proc = subprocess.Popen(command, **kwargs)
        proc.communicate()

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, command)

        return None


def get_vivitar_port(ports: Dict[str, str]):
    """
    Get vivitar port name based on port-id: device name mapping
    """
    KNOWN_NAMES = [
        "USB DIGITAL STILL CAMERA"
    ]

    for port_id, (device, _) in ports.items():
        for name in KNOWN_NAMES:
            if name.lower() in device.lower():
                return port_id
    return None


if __name__ == '__main__':
    print("Checking usbipd")
    try:
        try_run(["usbipd", "--version"])
    except subprocess.CalledProcessError:
        raise Exception("usbpid is not working, try installing it from https://github.com/dorssel/usbipd-win/releases")

    print("Checking WSL")
    try:
        try_run(["wsl", "--version"], use_stdout=False)
    except subprocess.CalledProcessError:
        raise Exception("WSL is not working, please install it and set it up\n"
                        "Make sure the default WSL distro is the one you would like to use (e.g. Ubunbtu)")

    print("Setting up USB communication")
    try:
        # these commands need root privileges
        cmd = "apt install linux-tools-generic hwdata && " \
              "update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20"
        try_run(f"wsl -u root sh -c \"{cmd}\"")
    except subprocess.CalledProcessError:
        raise Exception("Failed to setup USB communication in WSL")

    print("Reading USB ports")
    try:
        output = try_run(["usbipd", "wsl", "list"], use_stdout=False, print_output=True)
        header, *ports = output.split("\n")

        busid_end    = header.index("VID:PID")
        device_start = header.index("DEVICE")
        device_end   = header.index("STATE")
        ports = {
            port[:busid_end].strip(): (port[device_start:device_end].strip(), port[device_end:].strip())
            for port in ports if port.strip()
        }
    except subprocess.CalledProcessError:
        raise Exception("Failed to setup USB communication in WSL")

    port_id = get_vivitar_port(ports)
    if port_id is None:
        while True:
            port_id = input("Please enter the port ID that corresponds to the Vivitar Mini Camera").strip()
            if port_id in ports:
                break
    else:
        print(f"Using USB port {port_id}")

    if ports[port_id][1] != "Not attached":
        # detach port from whatever it was attached to
        print(f"Detaching port {port_id}")
        try:
            try_run(["usbipd", "wsl", "detach", "--busid", port_id])
        except subprocess.CalledProcessError:
            raise Exception("Error detaching USB port")

    print("Attaching port to WSL")
    try:
        try_run(["usbipd", "wsl", "attach", "--busid", port_id])
    except subprocess.CalledProcessError:
        raise Exception("Error attaching USB port to WSL")

    print("Listing WSL USB devices")
    try:
        try_run(["wsl", "lsusb"])
    except subprocess.CalledProcessError:
        raise Exception("Error listing WSL USB devices")

    print("Checking gphoto2")
    try:
        try_run(["wsl", "gphoto2", "--version"])
    except subprocess.CalledProcessError:
        if ALLOW_INSTALLATIONS:
            print("Installing gphoto2")
            try:
                # this command need root privileges
                cmd = "apt install gphoto2"
                try_run(["wsl", "-u", "root", "apt", "install", "gphoto2"])
            except subprocess.CalledProcessError:
                raise Exception("Error installing gphoto2")
        else:
            raise Exception("Please install gphoto2 in WSL")

    print("Exporting photos to temporary directory")
    with tempfile.TemporaryDirectory() as tmpdirname:
        dest = Path(tmpdirname).absolute()
        try:
            try_run(["wsl", "-u", "root", "gphoto2", "--auto-detect", "-P"], cwd=dest)
        except subprocess.CalledProcessError:
            raise Exception("Error exporting photos")

        print("Select photo destination")
        destination = easygui.diropenbox("Select a location to save the files", default="./")

        print("Converting photos")
        for file in os.listdir(tmpdirname):
            im = Image.open(Path(tmpdirname) / file)
            name = os.path.splitext(file)[0]
            im.save(Path(destination) / f"{name}.{SAVE_EXT}")

    if DELETE_PHOTOS:
        print("Deleting photos from camera")
        try:
            try_run(["wsl", "-u", "root", "gphoto2", "--auto-detect", "-D"], cwd=dest)
        except subprocess.CalledProcessError:
            raise Exception("Error deleting photos from camera")

