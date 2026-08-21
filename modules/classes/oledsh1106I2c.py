import sh1106
from machine import Pin, I2C

# Especificar si los pines Sda y Scl llevan pull-up o pull-down.
# Algunos módulos no traen las resistencias y hay que especificarlas en el código.

# Esta clase se escribe para mc que tengan I2c por hardware, como el ESP32, RP2040, etc.
# Esto contempla la mayoría de los mc

class Oled1106I2c:
    def __init__(self, sda_pin: int, scl_pin: int, width: int = 128, height: int = 64, i2c_freq: int = 400000):
        self.i2c = I2C(0, scl=Pin(scl_pin, Pin.IN, Pin.PULL_UP), sda=Pin(sda_pin, Pin.IN, Pin.PULL_UP), freq=i2c_freq)
        self.oled = sh1106.SH1106_I2C(width, height, self.i2c)

    def clear(self):
        self.oled.fill(0)
        self.oled.show()

    def display_text(self, text: str, x: int = 0, y: int = 0):
        self.oled.text(text, x, y)
        self.oled.show()

    def display_image(self, image):
        # Assuming 'image' is a bytearray or similar format compatible with the SH1106 driver
        self.oled.blit(image, 0, 0)
        self.oled.show()

