import socket
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
# Protocol is a base class that sets a layout for the Pixelflut protocol
# Client is a class that wraps around the Protocol class and implements its features via socketrs.

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
        print(f"[*] Processing chunk: {repr(image_chunk)}")
        print(count)
        width, height = image_chunk.size
        offset = count * width
        for y in range(height):
            for x in range(width):
                r,g,b = image_chunk.getpixel((x,y))
                self.s_draw_pixel(offset + x,y,r,g,b,255)


    def draw_image(self, image_path: str):
        original_image = Image.open(image_path)
        original_image.thumbnail(self.size)
        width, _ = original_image.size
        chunks = self.make_chunks(original_image)
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            
            for i, chunk in enumerate(chunks):
                future = executor.submit(self.process_chunk, chunk, i)
                future.result()

                
def main():
    host = "pixelflut.uwu.industries"
    port = 1234
    thread_count = 4
    client = PixelflutClient((host, port))
    print(f"[INFORMATION]\nHOST: {host}\nPORT: {port}\nTHREAD COUNT: {thread_count}\nCANVAS SIZE: {client.size}")
    #client.s_draw_rect(0,0,1280,720,255,255,255,255)
    client.draw_image("../Pictures/wallpaper_nord.png")
if __name__ == "__main__":
    main()
