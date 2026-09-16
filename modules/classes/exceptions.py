"""
Class Name : Several classes of exceptions
Version: 1.0
Author: Atilio Porfirio
Purpose: Customized exceptions for the library
Date Creation: 24-07-2026
Last Modified: 15-09-2026
-------------------------------------------------------

This is a module that contains several classes of exceptions used in the library.
Each exception class is designed to handle specific error scenarios related to different components,
such as I2C communication, OLED display, menu handling, and button interactions.
License: MIT
Dependencies:
    Exception class
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Hardware design:
Additional Note:

Example:
    def __init__(self, callback)
    self.callback = callback

    def _localCallback(self, tipoClick: int) -> None:
        try:
            self.callback(tipoClick)
        except Exception as e:
            raise ButtonException(f"Error calling callback: {self.callback.__name__}", "")
        finally:
            self._isrEnable = 1

"""

class MyException(Exception):
    def __init__(self, msg: str, code: str) -> None:
        self.code: str = code
        self.msg: str = msg
        super().__init__(f"Error: {self.msg}: code:{self.code}")

class I2cException(MyException):
    pass

class OledException(MyException):
    pass

class MenuException(MyException):
    pass

class ButtonException(MyException):
    pass

class EncoderException(MyException):
    pass

class InputException(MyException):
    pass