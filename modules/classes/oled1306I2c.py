"""
Class Name : Oled1306I2c
Version: 1.0
Author: Atilio Porfirio
Purpose: oled-based display driver
Date Creation: 24-07-2026
Last Modified: 06-08-2026
-------------------------------------------------------

Oled1306I2c is a MicroPython class to manage OLED displays connected via I2C
interface

Features:
    SSD1306_I2C subclass
    Simplifies the use of the display by providing methods to write and delete
    lines and characters controlling oled boundaries
License: MIT
Dependencies:
    ssd1306
    micropython
    machine
    exceptions
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Hardware design:
    The class relies on I2C hardware interface of the MC, thus, verify that
    the MC has I2C hardware interface before using this class.
    Most MC have I2C hardware interface.
    IMPORTANT !!!
        This class doesn't implement software pull-up / down thus external pull-up / down
        resistor must be used in the circuit if the module doesn't have them.
Example:
    from oled1306I2c import Oled1306I2c

    MyOled = Oled1306I2c(0, 1) # sda pin = 0, scl pin = 1
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

from ssd1306 import SSD1306_I2C
from machine import Pin, I2C
from exceptions import I2cException, OledException
from micropython import const


class Oled1306I2c(SSD1306_I2C):
    WIDTH = const(128)  # oled width if no specified
    HEIGHT = const(64)  # oled height if no specified
    FREQ = const(400000)  # oled i2c frequency if no specified
    LINE_HEIGHT = const(8)  # height in pixels of standard font used by the oled
    MAXLINE = const(HEIGHT // LINE_HEIGHT)  # maximum number of lines that can be written on the oled
    COLUMN_WIDTH = const(8)  # width in pixels of standard font used by the oled
    MAX_COLUMN = const(WIDTH // COLUMN_WIDTH)  # maximum number of columns that can be written on the oled

    def __init__(self, sda_pin: int, scl_pin: int, width: int = None, height: int = None, i2c_freq: int = None) -> None:
        """
        Initialize the OLED display.

        Parameters:
            sda_pin (int):
                The GPIO pin number for the SDA line.

            scl_pin (int):
                The GPIO pin number for the SCL line.

            width (int, optional):
                The width of the OLED display. Defaults to 128.

            height (int, optional):
                The height of the OLED display. Defaults to 64.

            i2c_freq (int, optional):
                The I2C frequency. Defaults to 400000 Hz.

            Raises: I2cException: If there is an error initializing the I2C interface.
        """
        self.width = Oled1306I2c.WIDTH if width is None else width
        self.height = Oled1306I2c.HEIGHT if height is None else height
        self.i2c_freq = Oled1306I2c.FREQ if i2c_freq is None else i2c_freq
        try:
            self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=self.i2c_freq)
            super().__init__(self.width, self.height, self.i2c)
        except Exception as e:
            raise I2cException(f"Error assigning I2C {e}") from e

    def _line_y(self, line: int) -> int:
        """
        Returns the y-coordinate in pixels for the specified line number.
        """
        return (line - 1) * Oled1306I2c.LINE_HEIGHT

    def _col_x(self, col: int) -> int:
        """
        Returns the x-coordinate in pixels for the specified column number.
        """
        return (col - 1) * Oled1306I2c.COLUMN_WIDTH

    def _valid_line(self, line: int) -> bool:
        """
        Validates if the specified line number is within the OLED display boundaries.
        """
        if not (line < 1 or line > Oled1306I2c.MAXLINE):
            return True
        raise OledException("Line is outside Oled boundaries")

    def _valid_column(self, column: int) -> bool:
        """
        Validates if the specified column number is within the OLED display boundaries.
        """
        if not (column < 1 or column > Oled1306I2c.MAX_COLUMN):
            return True
        raise OledException("Column is outside Oled boundaries")

    def write_lines(self, lines: list) -> None:
        """
        Writes the specified lines to the OLED display.
        Parameters:
            lines (list): A list of tuples, where each tuple contains a line number and the
            text to be written on that line.
        """
        for line, text in lines:
            self._valid_line(line)
            self.fill_rect(0, self._line_y(line), self.width, Oled1306I2c.LINE_HEIGHT, 0)
            if text:
                self.text(text[0 : Oled1306I2c.MAX_COLUMN], 0, self._line_y(line), 1)
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
        self._valid_line(line) and self._valid_column(col)
        self.fill_rect(self._col_x(col), self._line_y(line), len(chars) * Oled1306I2c.COLUMN_WIDTH, Oled1306I2c.LINE_HEIGHT, 0)
        self.text(chars[0 : Oled1306I2c.MAX_COLUMN - col + 1], self._col_x(col), self._line_y(line), 1)
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
