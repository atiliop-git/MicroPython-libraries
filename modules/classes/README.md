# <center>MicroPython Library</center>

## Key Features:
These library modules are designed using POO to facilitate the management of common devices in electronics projects using microcontrollers GPIO, programmed in MicroPython.
Its design relies on a compact isr code, and external user defined callbacks to handle the irq events.

## Electronic design Requirements
### Low-Pass filters and Pull-Up/Down resistors
While these libraries were created with simplicity and efficiency in mind, they do not include code to prevent bouncing in buttons, encoders, and other devices susceptible to this problem. It is well known that much better solutions exist for these problems using electronic components, such as low-pass filters to prevent bounce, for example.
Another design concept is the decision to base the function of the controllers on the use of external pull-up/pull-down resistors on the GPIO pins, to give projects greater design flexibility.

## Project Structure
This library is made by modules. Each module contains the classes needed to drive a single device.
The documentation of each class is written in the module file.  
The main characteristics of the modules of this library, are shown below

## Classes

### Button
Class to manage short and long clicks events on buttons connected to a GPIO microcontrollers
#### Main features
>* Irq driven
>* Trigger on high or low value
>* Normal Close or Normal Open buttons
>* Detect short or long clicks (Long click duration specified in the instantiation)
>* Uses an external (outside ISR context) user callback
>* No limit for the external user callback

### Encoder
Class to manage mechanical quadrature rotary encoders connected to GPIO microcontrollers
#### Main features
>* Irq driven
>* Detects clockwise and counter-clockwise rotation, and passes the direction to an external (outside the ISR context) user callback
>* No limit for the external user callback
### Oled1306I2c
Class to manage the oled 1306 with I2C interface
The class is a subclass of the existent SSD1306_I2C class
#### Main features
Helps and make very easy to display lines and chars on the oled
Implements controls to avoid overwrites of data
### Menu
Manages menu structures for OLED displays with no limit on the number of menus or submenus.
There is a limit in the amount of Items of a menu, which is determined by the OLED display size.
The class will raise an exception if the menu structure exceeds the display capacity.

### ButtonException, I2cException, OledException, MenuException
Customized Exception for different classes in this library

## Examples
### Button
```Python
from button import Button

MyButton = Button(4,500,Button.ACTIVE_HIGH, buttonpressed)
# button pin = 4
# Long click duration in ms = 500
# button activates on high value
    
def buttonpressed(longClick):
    if longClick == Button.LONG_CLICK:
       print('Long Click Detected')
    else:
       print('Short Click detected')
```
### Encoder
``` Python
    from encoder import Encoder

    Miencoder = Encoder(4,5,rotation)

    def rotation(direction):
        if direction == Encoder.CLOCKWISE:
            print('clockwise rotation detected')
        else:
            print('counterclockwise rotation detected')

```
### Oled1306I2c
``` Python
from oled1306I2c import Oled1306I2c

myOled = Oled1306I2c (sda_pin = 10, scl_pin = 11)

myOled.write_lines(((1,'linea 1'), (2, 'linea 2')))
myOled.delete_lines(1,2)
myOled.write_chars(line, col, 'xy')
myOled.delete_chars(line, col, num_of_chars)
myOled.clear_screen()
```
### Menu
```Python
    from menu import Menu
    from oled1306I2c import Oled1306I2c
    from encoder import Encoder
    from button import Button

    def muestra_algo(menu, item):
    print(f'hizo click en menu {menu} item {item}')
    menu = (
            ('Electr. Charge',   # menu #1
                (
                    (2,'Setup Values', 2, None, 'Click to enter', True),
                    (3,'Run/Stop', 0, muestra_algo, 'Run/Stop charge', True)
                ),
            ),
            (   # menu #2
                'Set Parameters',
                (
                    (2,'Set Current', 0, None, 'Current value', True),
                    (3,'Set Power', 0, None, 'Power value', True),
                    (4,'Set Resistance', 0, None, 'Resistance value', True),
                    (5,'Set min Voltage', 0, None, 'Low Volt Value', True),
                    (6,'Set time limit', 0, None, 'Run Time Limit', True),
                    (7,'Return', 1, None, 'Main Menu', True),
                )
                )
    )
    def set_cursor_position(direction):
        if direction == Encoder.CLOCKWISE:
            Main_menu.next_item()
        else:
            Main_menu.previous_item()
    def execute_item(long_short_click: int) -> None:
        if long_short_click == Button.SHORT_CLICK:
            Main_menu.execute_item()
        else:
            Main_menu.previous_menu()
    callback_encoder: callable = set_cursor_position
    callback_button: callable = execute_item
    e = Encoder(4,5,callback_encoder)
    b = Button(6, 400, 0, callback_button)
    oled = Oled1306I2c(sda_pin = 0, scl_pin = 1)
    Main_menu = Menu (oled, menu)
    Main_menu.show()
    Main_menu.select_item()
    while True:
        pass


```
## Hardware Design
### Buttons
Recommended hardware connection for buttons.
Low-Pass filter and Pull-up is needed
![Button](image.png)
### Rotary encoders
Recommended hardware connection for mechanical rotary encoders.
There is Low-Pass filters and Pull-Up resistors in each GPIO pins
![Encoder](image-1.png)
### Oled displays
>**For oled displays using I2C interface, it's recommended to check if the >Sda and Scl pins are pulled-Up in the module itself.
>Otherwise, defining Pin.PULL_UP is needed when the i2c object is >instantiated inside the Oled1306I2c class constructor, as is shown below**
```Python
    def __init__(self, sda_pin: int, scl_pin: int, width: int = None,
            height: int = None, i2c_freq: int = None) -> None:
        self.width = Oled1306I2c.WIDTH if width is None else width
        self.height = Oled1306I2c.HEIGHT if height is None else height
        self.i2c_freq = Oled1306I2c.FREQ if i2c_freq is None else i2c_freq
        try:
            self.i2c = I2C(0, sda=Pin(sda_pin, Pin.IN, Pin.PULL_UP), scl=Pin(scl_pin, Pin.IN, Pin.PULL_UP), freq=self.i2c_freq)
            super().__init__(self.width, self.height, self.i2c)
        except Exception as e:
            raise I2cException (f'Error assigning I2C {e}') from e
```
### Exceptions
The exceptions.py module contains Exception classes to personalize exceptions for each class in this library 
***
## Library Compatibility
This library's modules were tested in a real hardware, based on a RP2040 Zero, but no changes are needed to run in other `MicroPython-based microcontrollers`

## Limitations
* No code for debouncing are implemented
* No embedded GPIO Pull-Up/Down are implemented in GPIO pins
* Designed exclusively for MicroPython-based microcontrollers

## Installation
Copy the .py file of the module(s) needed to the /lib folder of the microcontroller file system
See the examples above

## Upcoming Improvements
There are modules to be added to this library, such as:
* Data Input class
* Ina219 Volt and current sensor module class
* ZMPT101B voltage sensor module class

## License

MIT license