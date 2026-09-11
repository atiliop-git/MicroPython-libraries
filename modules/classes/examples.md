# <center>MicroPython Classes examples</center>
## Button class example
```Python
    from button import Button
    button_pin = 4
    Long_click = 500 # in ms
    button_activates = Button.ACTIVE_LOW
    def buttonpressed(type_of_Click):
        if type_of_Click == Button.LONG_CLICK:
            print('Long Click Detected')
        else:
            print('Short Click detected')
    MyButton = Button(button_pin, Long_click, button_activates, buttonpressed)
```
## Encoder class example
```Python
    from encoder import Encoder
    pin_a = 4
    pin_b = 5
    def rotation(direction):
        if direction == Encoder.CLOCKWISE:
            print('clockwise rotation detected')
        else:
            print('counterclockwise rotation detected')
    Miencoder = Encoder(pin_a, pin_b, rotation)
```

## Oled1306I2c class example
```Python
    from oled1306I2c import Oled1306I2c
    from machine import Pin, I2C
    I2c = I2C(id, sda = Pin(6), scl = Pin(7))
    my_oled = Oled1306I2c(I2c)
    my_oled.write_lines([(1, 'Linea 1'), (2, 'linea 2')]) # write line 1 and line 2
    my_oled.delete_lines(2, 3) # delete lines 2 and 3
    my_oled.write_chars(2, 10, 'yes') # write 'yes' in line 2 column 10
    my_oled.clear_screen() # clears the oled screen

    # Besides the methods of this class, all the methods of class SSD1306_I2C
```

## Menu class example
```Python
    '''
    menu structure:
        Menu Title,
        (line #, item-text, menu-link, callback, foot-text, Enabled, input_item)

    menu-link = activate #menu when execute_item. 0 means no menu to activate
    callback = call callback when activate_item. None means no callback to call
    input_item = item in the inputs dict 
    '''
    from menu import Menu
    menu = (
            ('Electr. Charge',   # menu #1
                (
                    (2,'Setup Values', 2, None, 'Click to enter', True, 0),
                    (3,'Run/Stop', 0, None, 'Run/Stop charge', True, 0)
                ),
            ),
            (   # menu #2
                'Set Parameters',
                (
                    (2,'Set Current', 0, None, 'Current value', True,0),
                    (3,'Set Power', 0, None, 'Power value', True, 2),
                    (4,'Set Resistance', 0, None, 'Resistance value', True, 0),
                    (5,'Set min Voltage', 0, input_volt, 'Low Volt Value', True, 1),
                    (6,'Set time limit', 0, None, 'Run Time Limit', True, 0),
                    (7,'Return', 1, None, 'Main Menu', True, 0),
                )
                )
    )
    # Navigates the menu with an rotary encoder
    def set_cursor_position(direction):
        if direction == Encoder.CLOCKWISE:
            Main_menu.next_item()
        else:
            Main_menu.previous_item()

    # Accepts the menu item selected with short click or go to previous menu
    # with long click
    def execute_item(long_short_click: int) -> None:
        if long_short_click == Button.SHORT_CLICK:
            Main_menu.execute_item()
        else:
            Main_menu.previous_menu()

    e = Encoder(4,5,set_cursor_position)
    b = Button(6, 400, 0, execute_item)
    oled = Oled1306I2c(sda_pin = 0, scl_pin = 1)

    Main_menu = Menu (oled, menu)
    Main_menu.show()
    Main_menu.select_item()

    while True:
        pass
```

## Data_input_encoder class example
```Python
from encoder import Encoder
from button import Button
from oled1306I2c import Oled1306I2c
from data_input import Data_input_encoder
import time

def disable_input_devices():
    # Disable encoders and buttons to change callbacks
    e.disable()
    b_1.disable()
    b_2.disable()

def enable_input_devices():
    # Enable encoders and buttons
    e.enable()
    b_1.enable()
    b_2.enable()

# Callbacks to manage all types of inputs
def set_input_numbers_callbacks():
    e.set_callback(set_number_values)
    b_1.set_callback(accept_values)
    b_2.set_callback(clear_values)

def initialize_input_context(input_item):
    # set input context
    D_input.set_item(input_item)
    D_input.prompt()

def set_Input_numbers_context(input_item: int) -> None:
    # set input context for numbers
    disable_input_devices()
    set_input_numbers_callbacks()
    enable_input_devices()
    initialize_input_context(input_item)

def input_numbers(input_item: int) ->None:
    set_Input_numbers_context(input_item)

# Input numbers handlers callbacks ---------------------------------------
def set_number_values(direction: int):
    if direction:
        D_input.step_up()
    else:
        D_input.step_down()

def clear_values(long_short_click: int):
    D_input.clear_values()

def accept_values(long_short_click: int) -> None:
    D_input.set_values()
"""
inputs structure
(
    data_type: Data_input_encoder.STRING | YES_NO | NUMBER
    coord: (row, col) of the data to be input
    prompt: (Text, row, col) Text, row and col of the prompt
    format: format of data
    limits: (min value, max value) allowed to be input
    step_up: value increment step 
    step_down: value decrement step
    list: list of values to choose from
    value: value stored in the item. float | string | YesNo
)
"""
inputs = (
    {'data_type': Data_input_encoder.NUMBER,
     'coord': (4,10),
     'prompt': ('Voltaje :', 4, 1),
     'format': '.1f',
     'limits': (0, 10),
     'step_up': 5,
     'step_down': 1,
     'list': ('a', 'b', 'c'),
     'value': 0.0
    }
)

e = Encoder(4,5,set_number_values)
b_1 = Button(6, 0, 0, accept_values)
b_2 = Button(7, 0, 0, clear_values)
oled = Oled1306I2c(sda_pin = 0, scl_pin = 1)
D_input = Data_input_encoder(oled, inputs)

while True:
    field = 1
    if inputs[field]['data_type'] == Data_input_encoder.NUMBER:
        input_numbers(field+1)
    while True:
        pass
```