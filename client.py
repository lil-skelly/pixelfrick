import socket
import argparse
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

# Protocol is a base class that sets a layout for the Pixelflut protocol
# Client is a class that wraps around the Protocol class and implements its features via socketrs.
parser = argparse.ArgumentParser(description="Fast and extensible Pixelflut Client")

parser.add_argument("--image", "-ig", required=True, help="Path to the image to draw")
parser.add_argument("--host", "-H", type=str, default="pixelflut.uwu.industries", help="Pixelflut host to connect to")
parser.add_argument("--port", "-P", type=int, default=1234, help="Pixelflut port")
parser.add_argument("--threads", "-T", type=int, default=4, help="Number of threads to use. (Refer to README.md for guidance)")
parser.add_argument("--background", "-bg", help="Wipe the current canvas by setting a background of color R:G:B")
parser.add_argument("--buffer", "-bf", type=int, default=256, help="Data buffer to use (default: 256)")

class Protocol:
    def draw_pixel(self, x, y, r, g, b, a):
        """Generates a valid Pixelflut Protocol command 
        to draw a pixel of color <color> at position <x, y>
        """
        if a == 255:
            return "PX %d %d %02x%02x%02x\n" % (x,y,r,g,b)
        else:
            return "PX %d %d %02x%02x%02x%02x\n" % (x,y,r,g,b,a) # include a

    def draw_rect(self, x, y, w, h, r, g, b, a):
        pixels = []
        for i in range(x, x+w):
            for j in range(y, y+h):
                pixels.append(self.draw_pixel(i, j, r, g, b, a))
        return pixels 
    
    def pixel_value(self, x: str | tuple, y: str | tuple):
        return f"PX {x} {y}\n"

class PixelflutClient(Protocol):
    sock = None
    size = (0, 0)

    def __init__(self, address: tuple[str, int], buffer: int = 256, thread_count = 4) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.BUFFER = buffer
        self.thread_count = thread_count
        self.address = address
        self.connect()

    def connect(self):
        """Connects to a Pixelflut server"""
        self.sock.connect(self.address)
        print(f"[*] Connected to <{self.address[0]}:{self.address[1]}>")
        self.size = self.canvas_size()

    def canvas_size(self) -> tuple[int, int]:
        """Returns the canvas size (x, y) of the Pixelflut server"""
        self.sock.send("SIZE\n".encode())
        size = self.sock.recv(self.BUFFER).decode().split(" ")
        return int(size[1]), int(size[2])
    
    def s_draw_pixel(self, *args):
        pixel = super().draw_pixel(*args)
        self.sock.send(pixel.encode())

    def s_draw_rect(self, *args):
        """
        Draws a rectangle
        [DEPRECATED] Use PixelflutClient.draw_image with a PIL image for performance.
        """
        print(f"[*] Drawing RECTANGLE: {args[0], args[1]}, {args[2], args[3]}") 
        pixels = super().draw_rect(*args)
        for pixel in pixels:
            self.sock.send(pixel.encode())
        print("[*] Done")

    def s_pixel_value(self, *args):
        pixel = super().pixel_value(*args)
        self.sock.send(pixel.encode())
        value = self.sock.recv(self.BUFFER).decode().split()[3:4]
        print(f"VALUE OF PIXEL ({args[0]}, {args[1]}): {value}")
    
    def make_chunks(self, image):
        """Divide the given image into equal chunks to feed to the thread pool"""
        width, height = image.size
        part_width = width // self.thread_count
        image_chunks = []
        
        for i in range(self.thread_count):
            left = i * part_width
            right = (i + 1) * part_width
            image_chunk = image.crop((left, 0, right, height))
            image_chunks.append(image_chunk)

        return image_chunks
    

    def process_chunk(self, image_chunk, count):
        """Draw each pixel from a chunk to the Pixelflut server"""
        width, height = image_chunk.size
        for y in range(height):
            for x in range(width):
                r,g,b = image_chunk.getpixel((x,y))
                self.s_draw_pixel(x + width * count,y,r,g,b,255)


    def draw_image(self, image):
        if isinstance(image, Image.Image):
            chunks = self.make_chunks(image)
        elif isinstance(image, str):
            original_image = Image.open(image)
            original_image.thumbnail(self.size)
            chunks = self.make_chunks(original_image)
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            for i, chunk in enumerate(chunks):
                future = executor.submit(self.process_chunk, chunk,i)
                future.result()

def apply_background(client: PixelflutClient, r,g,b):
    background = Image.new("RGB", client.size, (r,g,b))
    print(f"[*] Applying background {r,g,b}.")
    client.draw_image(background)
    print("[*] Done.")


def main():
    args = parser.parse_args()
    HOST = args.host 
    PORT = args.port
    THREADS = args.threads
    BUFFER = args.buffer
    client = PixelflutClient((HOST, PORT), BUFFER, THREADS)
    print(f"[INFORMATION]\nHOST: {HOST}\nPORT: {PORT}\nTHREAD COUNT: {client.thread_count}\nCANVAS SIZE: {client.size}")
    #client.s_draw_rect(0,0,1280,720,255,255,255,255)
    if args.background:
        r,g,b = args.background.split(":")
        apply_background(client, int(r), int(g), int(b))
    client.draw_image(args.image)


if __name__ == "__main__":
    main()
