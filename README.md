# Pixelfrick
Fast and extensible Python Pixelflut client made for fun

# Usage

## Installation
```bash
$ git clone https://github.com/CopernicusPY/pixelfrick
[ . . . ]
$ cd pixelfrick
$ python client.py --help
Fast and extensible Pixelflut Client

options:
  -h, --help            show this help message and exit
  --image IMAGE, -ig IMAGE
                        Path to the image to draw
  --host HOST, -H HOST  Pixelflut host to connect to
  --port PORT, -P PORT  Pixelflut port
  --threads THREADS, -T THREADS
                        Number of threads to use. (Refer to README.md for guidance)
  --background BACKGROUND, -bg BACKGROUND
                        Wipe the current canvas by setting a background of color R:G:B
  --buffer BUFFER, -bf BUFFER
                        Data buffer to use (default: 256)
```
Examples
```bash
$ python client.py --background 255:255:255 --threads 16 --image ../Pictures/kitty.png
[*] Connected to <pixelflut.uwu.industries:1234>
[INFORMATION]
HOST: pixelflut.uwu.industries
PORT: 1234
THREAD COUNT: 16
CANVAS SIZE: (1280, 720)
[*] Applying background (255,255,255) on canvas.
[*] Done.
```

# Documentation
* NOTE: If you use `pixelflut.uwu.industries:1234` please note that using more than `426` threads will cause missing chunks.
* I recommend using smaller thread counts for more consistent results, performance-wise. 
I am currently working to find the *sweetspot* of threads so stay tuned :)
* I plan on documenting the WHOLE thought process of the making of this project.
