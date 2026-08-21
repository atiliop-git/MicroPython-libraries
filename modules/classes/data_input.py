"""
Class Name : Data_input_encoder
Version: 1.0
Author: Atilio Porfirio
Purpose: Data input management using rotary encoder and buttons
Date Creation: 01-08-2026
Last Modified: 18-08-2026
-------------------------------------------------------

Data_input_encoder is a MicroPython class to manage data inputs using rotary encoders and buttons

Features:
    Manages data inputs using OLED displays, and rotary encoders and buttons
    It's usually used with Menu classes
    There is no limit in the amount of data fields to filling
    Its designs relies on the use of encoders, buttons, and a display as the peripherals used 
    to enter data to the fields and to see them on a display
    The class will raise an exceptions if the inputs structure contains inconsistent data
    The fields are defined in a tuple of disctionaries containing the type and other parameters
    of fields
License: MIT
Dependencies:
    exceptions
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Data input structure example:

inputs = (
    {'data_type': 2,
     'coord': (4,10),
     'prompt': ('Voltaje :', 4, 1),
     'format': ':.1f',
     'limits': (0, 30),
     'step_up': 5,
     'step-down': 1,
     'clear_screen': True,
     'value' : 0.0
    },
    .
    .
    .
)
Usage example:
    see README.md
"""
from micropython import const
from exceptions import InputException

class Data_input_encoder:
    """
    This class manages the data input for numbers, strings and Yes/No fields using
    interactive devices such as rotary encoders, buttons and an oled display
    It also receives control from menues driven by a Menu class
    """

    # Data types
    STRING = const(0)
    YES_NO = const(1)
    NUMBER = const(2)

    def __init__(self, oled, param: dict):
        self._oled = oled
        self._param = param
        self._value_num: float = float()
        self._value_str: str = ''
        self._value_yes_no: int = 0
        self._current_item: int = 0

    def _data_type(self) -> int:
        return self._param[self._current_item-1]['data_type']

    def _value_coords(self) -> tuple:
        return (self._param[self._current_item-1]['coord'][0], self._param[self._current_item-1]['coord'][1])

    def _prompt_coords(self) -> tuple:
        return (self._param[self._current_item-1]['prompt'][1], self._param[self._current_item-1]['prompt'][2])

    def _get_values(self):
        return (self._param[self._current_item-1]['value'])
    
    def prompt(self):
        """
        This method is used to display the prompt of the input.
        It obtains the prompt string from the inputs structure of the current input item 
        """
        if self._param[self._current_item-1]['clear_screen']:
            self._oled.clear_screen()
        self._oled.write_chars(*self._prompt_coords(), self._param[self._current_item-1]['prompt'][0])
        if self._data_type() == Data_input_encoder.NUMBER:
            value_format = f'{self._value_num:{self._param[self._current_item-1]["format"]}}'
            self._oled.write_chars(*self._value_coords(),value_format)
        elif self._data_type() == Data_input_encoder.STRING:
            self._oled.write_chars(*self._value_coords(),self._value_str)
        elif self._data_type() == Data_input_encoder.YES_NO:
            self._oled.write_chars(*self._value_coords(),'Yes' if self._value_yes_no else 'No')
        else:
            raise InputException('Invalid data type in module data_input')
    
    def set_item(self, item: int) -> None:
        """
        This method is used to setup the current item in the inputs structure
        The argument must be an integer corresponding to the position of
        the item in the inputs structure, startin with 1 for the first item
        It rises an exception if the type of the item is incorrect
        """
        self._current_item = item
        if self._data_type() == Data_input_encoder.NUMBER:
            self._value_num = self._get_values()
            self._value_str = ''
            self._value_yes_no = 0
        elif self._data_type() == Data_input_encoder.STRING:
            self._value_str = self._get_values()
            self._value_num = 0.0
            self._value_yes_no = 0
        elif self._data_type() == Data_input_encoder.YES_NO:
            self._value_yes_no = self._get_values()
            self._value_num = 0.0
            self._value_str = ''
        else:
            raise InputException('Invalid data type in module data_input')
    
    def clear_values(self):
        """
        This method is used to clear the value of the current item.
        However it doesn't update the stored value in the inputs structure 
        """
        self._value_num = 0.0
        self._value_str = ''
        self._value_yes_no = 0
        self.prompt()

    def set_values(self) -> None:
        """
        This method updates the stored value of the current item with
        the current value (the value shown on the display)
        It rises an exception if the type of the item is incorrect
        """
        if self._param[self._current_item-1]['data_type'] == Data_input_encoder.NUMBER:
            self._param[self._current_item-1]['value'] = self._value_num
        elif self._param[self._current_item-1]['data_type'] == Data_input_encoder.STRING:
            self._param[self._current_item-1]['value'] = self._value_str
        elif self._param[self._current_item-1]['data_type'] == Data_input_encoder.YES_NO:
            self._param[self._current_item-1]['value'] = self._value_yes_no
        else:
            raise InputException('Invalid data type in module data_input')

    def step_up(self) -> None:
        """
        This method is used to increase the current value of the current
        numeric item.
        The amount of increment is obtained from the inputs structure
        The value will not be greater than the maximum value defined in
        the inputs structure
        """
        self._value_num += self._param[self._current_item-1]['step_up']
        # Reemplazar el siguiente if con la función min(). Lo mismo en step_down()
        if self._value_num > self._param[self._current_item-1]['limits'][1]:
            self._value_num = self._param[self._current_item-1]['limits'][1]
        self.prompt()

    def step_down(self) -> None:
        """
        This method is used to decrease the current value of the current
        numeric item.
        The amount of decrement is obtained from the inputs structure
        The value will not be less than the minimum value defined in
        the inputs structure
        """
        self._value_num -= self._param[self._current_item-1]['step_down']
        if self._value_num < self._param[self._current_item-1]['limits'][0]:
            self._value_num = self._param[self._current_item-1]['limits'][0]
        self.prompt()
    
    def toggle_yes_no(self) -> None:
        """
        This method is used to toggle the value Yes/No of the Yes_No field
        in the current item
        """
        self._value_yes_no = not self._value_yes_no
        self.prompt()

    def read_text(self, text) -> None:
        """
        This method is used to setup the current value of the current item 
        with the text entered with any input method 
        """
        self._value_str = text
        self.prompt()
