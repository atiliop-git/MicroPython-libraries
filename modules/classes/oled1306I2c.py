"""
Class Name : Oled1306I2c
Version: 1.1
Author: Atilio Porfirio
Purpose: oled-based display driver
Date Creation: 24-07-2026
Last Modified: 26-09-2026
-------------------------------------------------------

Oled1306I2c is a MicroPython class to manage OLED displays connected via I2C
interface

Features:
    SSD1306_I2C subclass
    Simplifies the use of the display by providing methods to write and delete
    lines and characters controlling oled boundaries
    New in version 1.1: User can define fonts others than default font 8x8 through the Writer class
        from Peter Hinch https://github.com/peterhinch/micropython-font-to-py
License: MIT
Dependencies:
    ssd1306
    micropython
    exceptions
    writer
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Hardware design:
    The class relies on I2C hardware interface of the MC, thus, verify that
    the MC has I2C hardware interface before using this class.
    Most MC have I2C hardware interface.
Example:
    from oled1306I2c import Oled1306I2c
    from machine import Pin, I2C
    I2c = I2C(id, sda = Pin(6), scl = Pin(7))

    MyOled = Oled1306I2c(I2c) # Oled = oled interface object,sda pin = 0, scl pin = 1
    MyOled.write_lines([(1, 'Hello'), (2, 'World')])
    MyOled.write_chars(3, 5, 'MicroPython')
    MyOled.delete_lines(1, 2)
    MyOled.delete_chars(3, 5, 5)


Some superclass (SSD1306_I2C) functions reference:

text(x, y, color) # llena el buffer con el texto en la posicion indicada por x, y
poweroff()     # power off the display, pixels persist in memory
poweron()      # power on the display, pixels redrawn
contrast(0)    # dim
contrast(255)  # bright
invert(1)      # display inverted
invert(0)      # display normal
rotate(True)   # rotate 180 degrees
rotate(False)  # rotate 0 degrees
show()         # write the contents of the FrameBuffer to display memory
"""


from ssd1306 import SSD1306_I2C  # type: ignore
from exceptions import ButtonException, MyException, OledException  # type: ignore
from machine import I2C, Pin  # type: ignore
from micropython import const # type: ignore
try:
    from ast import Module
    from types import ModuleType
    from typing import Any
except ImportError:
    pass

class Oled1306I2c(SSD1306_I2C):
    # Default values for a standard Oled display of 128x64
    WIDTH = const(128)  # oled width if no specified
    HEIGHT = const(64)  # oled height if no specified
    FREQ = const(400000)  # oled i2c frequency if no specified
    LINE_HEIGHT = const(8)  # height in pixels of standard font used by the oled
    COLUMN_WIDTH = const(8)  # width in pixels of standard font used by the oled

    def __init__(self, i2c, width: int = 0, height: int = 0) -> None:
        """
        Initialize the OLED display.

        Parameters:
            width (int, optional):
                The width of the OLED display. Defaults to 128.

            height (int, optional):
                The height of the OLED display. Defaults to 64.

            Raises: OledException: If there is an error initializing the OLED display.
        """

        self.width = Oled1306I2c.WIDTH if width is 0 else width
        self.height = Oled1306I2c.HEIGHT if height is 0 else height
        self.i2c = i2c
        self.font_height: int = Oled1306I2c.LINE_HEIGHT
        self.font_width: int = Oled1306I2c.COLUMN_WIDTH
        self.max_lines: int = self.height // self.font_height
        self.max_columns: int = self.width // self.font_width
        self.font_module: str = ''
        try:
            super().__init__(self.width, self.height, self.i2c)
        except Exception as e:
            raise OledException('Error Init Oled', 'super().__init__()')

    def _line_y(self, line: int) -> int:
        """
        Returns the y-coordinate in pixels for the specified line number.
        """
        return (line - 1) * self.font_height

    def _col_x(self, col: int) -> int:
        """
        Returns the x-coordinate in pixels for the specified column number.
        """
        return (col - 1) * self.font_width

    def _valid_line(self, line: int) -> bool:
        """
        Validates if the specified line number is within the OLED display boundaries.
        """
        if not (line < 1 or line > self.max_lines):
            return True
        raise OledException("Invalid line number :",f'{line}')

    def _valid_column(self, column: int) -> bool:
        """
        Validates if the specified column number is within the OLED display boundaries.
        """
        if not (column < 1 or column > self.max_columns):
            return True
        raise OledException("Invalid column number :", f'{column}')

    def write_lines(self, lines: list) -> None:
        """
        Writes the specified lines to the OLED display.
        Parameters:
            lines (list): A list of tuples, where each tuple contains a line number and the
            text to be written on that line.
        """
        for line, text in lines:
            _: bool = self._valid_line(line)
            self.fill_rect(0, self._line_y(line), self.width, self.font_height, 0)
            if text:
                if self.font_module:
                    self.wri.set_textpos(self, self._line_y(line), 0)
                    self.wri.printstring(text[0 : self.max_columns])
                else:
                    self.text(text[0 : self.max_columns], 0, self._line_y(line), 1)
        self.show()

    def delete_lines(self, *lines: int) -> None:
        """
        Clears the specified lines
        Parameters:
            lines (int): A variable number of line numbers to be cleared.
        It receives a variable number of arguments with the lines to be erased
        call the class method write_lines with empty strings
        """
        self.write_lines([(i, "") for i in lines])

    def write_chars(self, line: int, col: int, chars: str) -> None:
        """
        Writes the specified characters to the OLED display at the given line and column.
        Parameters:
            line (int): The line number where the characters will be written.
            col (int): The column number where the characters will start.
            chars (str): The string of characters to be written.
        """
        if chars:
            _: bool = self._valid_line(line) and self._valid_column(col)
            self.fill_rect(self._col_x(col), self._line_y(line), len(chars) * self.font_width, self.font_height, 0)
            if self.font:
                self.wri.set_textpos(self, self._line_y(line), self._col_x(col))
                self.wri.printstring(chars[0 : self.max_columns - col + 1])
            else:
                self.text(chars[0 : self.max_columns - col + 1], self._col_x(col), self._line_y(line), 1)
            self.show()

    def delete_chars(self, line: int, col: int, n_chars: int) -> None:
        """
        Deletes the specified number of characters from the OLED display at the given line and column.
        Parameters:
            line (int): The line number where the characters will be deleted.
            col (int): The column number where the deletion will start.
            n_chars (int): The number of characters to be deleted.
        It receives the line and column where the deletion will start and the number of characters to be
        deleted, it calls the class method write_chars with a string of spaces to overwrite the characters
        """
        self.write_chars(line, col, " " * n_chars)

    def clear_screen(self) -> None:
        """
        Erases the whole screen
        It fills the whole screen with zeros and calls the show method to update the display
        """
        self.fill(0)
        self.show()
    
    def _set_boundaries(self, font_height: int, font_width: int) -> tuple:
        '''
        Calculates max line and column for the font_height and width defined
        '''
        return self.height // self.font_height, self.width // self.font_width
    
    def _set_font_default(self) -> None:
        '''
        Sets the default values of font height and width and display boundaries for printing
        '''
        self.font_height = 8   
        self.font_width = 8
        self.max_lines, self.max_columns = self._set_boundaries(self.font_height, self.font_width)
    
    def set_font(self, font_module: str) -> None:
        '''
        Sets a new font for the diaplay
        The font must be a python font (a .py file) created using font-to-py desktop program
        If empty string is passed as argument, the default Framebuffer font is used
        New boundaries for the display are calculated using the font size (height and width)
        If other than the default font is set, the Writer class and the font file are imported, and so,
        the printstring method of the class Writer is used to display text in the display, 
        instead the text method from class Framebuffer
        '''
        self.font_module = font_module
        if self.font_module:
            try:
                self.font= __import__(font_module)
                from writer import Writer
                self.wri: Writer = Writer(self, self.font, verbose=False)
                self.font_height = self.font.height()
                self.font_width = self.font.max_width()
                self.max_lines, self.max_columns = self._set_boundaries(self.font_height, self.font_width)
                # print(f'{self.max_lines=} - {self.max_columns=}')
                # print(f'{self.font_height=} - {self.font_width=}')
            except ImportError:
                print("Font file doesn't exist")
                self._set_font_default()
        else:
            self._set_font_default()
            