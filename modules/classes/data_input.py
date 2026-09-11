"""
Class Name : Data_input_encoder
Version: 1.0
Author: Atilio Porfirio
Purpose: Data input management using rotary encoder and buttons
Date Creation: 01-08-2026
Last Modified: 11-09-2026
-------------------------------------------------------

Data_input_encoder is a MicroPython class to manage data inputs using rotary encoders and buttons

Features:
    Manages data inputs using OLED displays, and rotary encoders and buttons
    It's usually used with Menu classes or alone to enter values to a program from input devices
    There is no limit in the amount of data fields to filling
    Its designs relies on the use of encoders, buttons, and a display as the peripherals used
    to enter data to the fields and to see them on a display
    The class will raise an exceptions if the inputs structure contains inconsistent data
    The fields are defined in a tuple of disctionaries containing the type and other parameters
    of fields
    The type list allows to choose  a value among a list of string elements
License: MIT
Dependencies:
    exceptions
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Data input structure example:

inputs: tuple[dict, ...] = (
    {
    'data_type': 2,
    'coord': (4,10),
    'prompt': ('Voltaje :', 4, 1),
    'format': ':.1f',
    'limits': (0, 30),
    'step_up': 5,
    'step-down': 1,
    'list': (),
    'value' : 0.0
    },
    ...

Usage example:
    see README.md
"""

from micropython import const # type: ignore
from exceptions import InputException
from oled1306I2c import Oled1306I2c

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
    LIST = const(3)

    def __init__(self, oled: Oled1306I2c, param: tuple[dict, ...]) -> None:
        self._oled = oled
        self._param = param
        self._value_num: float = float()
        self._value_str: str = ''
        self._value_yes_no: int = 0
        self._current_item: int = 0
        self._current_list_item: int = 0
        self._max_list_item: int = 0

    def _data_type(self) -> int:
        return self._param[self._current_item-1]['data_type']

    def _value_coords(self) -> tuple[int, int]:
        return (self._param[self._current_item-1]['coord'][0], self._param[self._current_item-1]['coord'][1])

    def _prompt_coords(self) -> tuple[int, int]:
        return self._param[self._current_item-1]['prompt'][1], self._param[self._current_item-1]['prompt'][2]

    def _get_values(self):
        return self._param[self._current_item-1]['value']
    
    def _get_lista_item(self):
        return self._param[self._current_item-1]['list'][self._current_list_item - 1]

    def _set_cursor(self, cursor: str) -> None:
        """
        This method is used to set the cursor in the display at the position of the current value
        """
        self._oled.write_chars(self._prompt_coords()[0], 1, cursor[:1])

    def prompt(self) -> None:
        """
        This method is used to display the prompt of the input.
        It obtains the prompt string from the inputs structure of the current input item 
        """
        self._oled.write_chars(self._prompt_coords()[0], self._prompt_coords()[1]+1, self._param[self._current_item-1]['prompt'][0][0:16])
        if self._data_type() == Data_input_encoder.NUMBER:
            value_format = f'{self._value_num:{self._param[self._current_item-1]["format"]}}'
            self._oled.write_chars(*self._value_coords(),value_format)
        elif self._data_type() == Data_input_encoder.STRING:
            string_format = f'{self._value_str:{self._param[self._current_item-1]["format"]}}'
            self._oled.write_chars(*self._value_coords(),string_format)
        elif self._data_type() == Data_input_encoder.YES_NO:
            self._oled.write_chars(*self._value_coords(),'Yes' if self._value_yes_no else 'No ')
        elif self._data_type() == Data_input_encoder.LIST:
            string_format = f'{self._get_lista_item():{self._param[self._current_item-1]["format"]}}'
            self._oled.write_chars(*self._value_coords(),string_format)
        else:
            raise InputException('Invalid data type in module data_input')
    
    def set_item(self, item: int) -> None:
        """
        This method is used to setup the current item in the inputs structure
        The argument must be an integer corresponding to the position of
        the item in the inputs structure, startin with 1 for the first item
        It rises an exception if the type of the item is incorrect
        """
        self._set_cursor(' ')
        self._current_item = item
        self._set_cursor('-')
        if self._data_type() == Data_input_encoder.NUMBER:
            self._value_num = self._get_values()
        elif self._data_type() == Data_input_encoder.STRING:
            self._value_str = self._get_values()
        elif self._data_type() == Data_input_encoder.YES_NO:
            self._value_yes_no = self._get_values()
        elif self._data_type() == Data_input_encoder.LIST:
            self._current_list_item = self._get_values()
            self._max_list_item = len(self._param[self._current_item - 1]['list'])
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
        self._current_list_item = 0
        self.prompt()

    def set_values(self) -> None:
        """
        This method updates the stored value of the current item with
        the current value (the value shown on the display)
        It rises an exception if the type of the item is incorrect
        """
        if self._data_type() == Data_input_encoder.NUMBER:
            self._param[self._current_item - 1]['value'] = self._value_num
        elif self._data_type() == Data_input_encoder.STRING:
            self._param[self._current_item - 1]['value'] = self._value_str
        elif self._data_type() == Data_input_encoder.YES_NO:
            self._param[self._current_item - 1]['value'] = self._value_yes_no
        elif self._data_type() == Data_input_encoder.LIST:
            self._param[self._current_item - 1]['value'] = self._current_list_item
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
        self._value_num = min (self._value_num + self._param[self._current_item - 1]['step_up'], self._param[self._current_item - 1]['limits'][1])
        self.prompt()

    def step_down(self) -> None:
        """
        This method is used to decrease the current value of the current
        numeric item.
        The amount of decrement is obtained from the inputs structure
        The value will not be less than the minimum value defined in
        the inputs structure
        """
        self._value_num = max (self._value_num - self._param[self._current_item - 1]['step_down'], self._param[self._current_item - 1]['limits'][0])
        self.prompt()
    
    def list_up(self) -> None:
        """
        This method is used to select the next value of the current
        list item.
        """
        self._current_list_item = self._current_list_item + 1 if self._current_list_item < self._max_list_item else 1
        self.prompt()

    def list_down(self) -> None:
        """
        This method is used to select the previous value of the current
        list item.
        """
        self._current_list_item = self._current_list_item - 1 if self._current_list_item > 1 else self._max_list_item
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

    def get_values(self) -> tuple[float, str, int]:
        """
        This method is used to return the current value of current item
            
        """
        return (self._value_num, self._value_str, self._value_yes_no)
