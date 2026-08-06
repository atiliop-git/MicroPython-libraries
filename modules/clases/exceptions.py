"""
Class Name : Several classes of exceptions
Version: 1.0
Author: Atilio Porfirio
Purpose: Customized exceptions for the library
Date Creation: 24-07-2026
Last Modified: 06-08-2026
-------------------------------------------------------

This is a module that contains several classes of exceptions used in the library.
Each exception class is designed to handle specific error scenarios related to different components,
such as I2C communication, OLED display, menu handling, and button interactions.
License: MIT
Dependencies:
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Hardware design:
Additional Note:

Example:

    def _localCallback(self, tipoClick: int) -> None:
        try:
            self.callback(tipoClick)
        except Exception as e:
            raise ButtonException(f"Error calling callback {self.callback.__name__} {e}") from e
        finally:
            self._isrEnable = 1

"""


class I2cException(Exception):
    pass


class OledException(Exception):
    pass


class MenuException(Exception):
    pass


class ButtonException(Exception):
    pass
