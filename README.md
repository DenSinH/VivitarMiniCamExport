# VivitarMiniCamExport
Small repository to explain / automatically export photos from a Vivitar Mini Camera

We found this mini camera that can go on your keychain, a Vivitar Mini Camera, but we had no way of extracting the photos. Online tutorials only showed people using
Windows XP machines to install the official software, but after some digging through online forums, I found a way to do it in an "easier" way, just on Windows 10.

The steps to do it are in windows.md, and I also wrote a script to do it automatically for me, in windows.py.

I might write a script to do it on Mac and Linux, but it is a lot easier on those platforms.

## Extracting Photos on Mac

To do this, install `brew`, and then use brew to install `gphoto2`. Then you can simply run the commmand
```
sudo gphoto2 --auto-detect -P
```
to extract all photos to the current folder. They are extracted as `.ppm` files, so you could use (part of) the Windows script
(using Pillow) to convert the images to png (or whatever format you like).

To delete the photos off the camera, run the command
```
sudo gphoto2 --auto-detect -D
```

## Extracting Photos on Linux

This should effectively be the same as on Mac, just install `gphoto2` and run the commands described above.
