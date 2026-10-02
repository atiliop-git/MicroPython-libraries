"""
Class Name : Button
Version: 1.0
Author: Atilio Porfirio
Purpose: mechanical button driver
Date Creation: 24-07-2026
Last Modified: 02-10-2026
-------------------------------------------------------

Button is a MicroPython call to manage mechanical buttons connected to a GPIO of a MC

Features:
    IRQ driven
License: MIT
Dependencies:
    machine
    micropython
    exceptions
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Hardware design:
    The class relies on either low or high level pin activation.
    This class doesn't implement software pull-up / down thus external pull-up / down
    resistor must be used in the circuit
    No debouncing implementation was included in its design.
    It's strongly recommended to use hardware debouncing methods such as low-pass filter
    made by a resistor and a capacitor, and schmitt trigger if needed

Example:

    from button import Button

    def buttonpressed(clickType):
        if clickType == Button.LONG_CLICK:
            print('Long Click Detected')
        elif clickType == Button.DOUBLE_CLICK:
            print('Double Click Detected')
        else:
            print('Short Click detected')

    MyButton = Button(4,Button.ACTIVE_HIGH, buttonpressed)

    # button GPIO pin = 4
    # button activates on high value
    # Callback function "buttonpressed"
    # Long click duration in ms = 400 ms (default value)
    # button double click = 200 ms (default value)

"""

from micropython import const, alloc_emergency_exception_buf, schedule # type: ignore
from machine import Pin, Timer # type: ignore
from exceptions import ButtonException
try:
    from typing import Callable
except ImportError:
    pass

alloc_emergency_exception_buf(200)

class Button:
    """
    Driver for mechanical button

    The class detects button click using GPIO interrupt and schedules a callback
    function outside isr context, passing short, long or double click as an argument
    """

    SHORT_CLICK: int = const(0)
    LONG_CLICK: int = const(1)
    DOUBLE_CLICK: int = const(2)
    ACTIVE_HIGH: int = const(1)
    ACTIVE_LOW: int = const(0)

    def __init__(self, pin: int, upDown: int, callback: Callable , longClick_ms: int = 400, doubleClick_ms: int = 200) -> None:
        """
        Creates a Button object

        Parameters:
            pin (int):
                GPIO connected to the button

            upDown (int):
                Level of activation.
                Button.ACTIVE_HIGH for a button that activates on high level
                Button.ACTIVE_LOW for a button that activates on low level

            callback (callable):
                Function to schedule when click is detected
                Receives SHORT_CLICK, LONG_CLICK or DOUBLE_CLICK

            longClick_ms (int):
                Duration of a long click in milliseconds
                Must be >= 100 ms

            doubleClick_ms (int):
                Time elapsed to consider two clicks as double click, in ms
                Must be >= 100 ms

        Raises:
            TypeError / ValueError:
                if any parameter is invalid
        """
        if not isinstance(longClick_ms, int) or isinstance(longClick_ms, bool):
            raise TypeError("longClick_ms must be int")

        if not isinstance(doubleClick_ms, int) or isinstance(doubleClick_ms, bool):
            raise TypeError("doubleClick_ms must be int")

        if longClick_ms < 300:
            raise ValueError(f"longClick_ms must be >= 300 ms")

        if doubleClick_ms < 150:
            raise ValueError(f"doubleClick_ms must be >= 150 ms")

        if longClick_ms <= doubleClick_ms:
            raise ValueError(f"longClick_ms must be greater than doubleClick_ms")
        
        self._longClick_ms = longClick_ms

        self._doubleClick_ms = doubleClick_ms

        if not isinstance(pin, int) or pin < 0:
            raise TypeError("Pin must be an integer >= 0")
        self._pin = pin

        if upDown not in (Button.ACTIVE_HIGH, Button.ACTIVE_LOW):
            raise ValueError("upDown must be Button.ACTIVE_HIGH or Button.ACTIVE_LOW")
        self._upDown = upDown

        if not callable(callback):
            raise TypeError("callback must be a defined function")
        self.callback: Callable = callback

        # Variables globales del objeto
        self._pinButton = Pin(self._pin, Pin.IN)
        self._pinButton.irq(handler=self.buttonPressed, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self._isrEnable = 1
        self._timer_doubleClick_Running: int = 0
        self._timer_doubleClick: Timer = Timer(-1)
        self._timer_longClick: Timer = Timer(-1)
        self._longClick_fired: bool = False
        self._doubleClick_fired: bool = False
        
    def _timer_doubleClick_Start (self) -> None:
        self._timer_doubleClick.init(period=self._doubleClick_ms, mode = Timer.ONE_SHOT, callback=self._callback_doubleClick_timer)
        self._timer_doubleClick_Running = 1
    
    def _timer_longClick_Start (self) -> None:
        self._timer_longClick.init(period=self._longClick_ms, mode = Timer.ONE_SHOT, callback=self._callback_longClick_timer)
    
    def _callback_doubleClick_timer(self, t: Timer) -> None:
        try:
            self._timer_doubleClick_Running = 0
            schedule(self.callback ,Button.SHORT_CLICK)
        except Exception as e:
            print('Calling self.callback en _callback_doubleClick_timer', e)
    
    def _callback_longClick_timer(self, t: Timer) -> None:
        try:
            self._longClick_fired = True
            schedule(self.callback, Button.LONG_CLICK)
        except Exception as e:
            print('Calling self.callback en _callback_longClick_timer', e)

    def _localCallback_clickDown(self, _) -> None:
        try:
            if self._timer_doubleClick_Running:
                self._timer_doubleClick.deinit()
                self._timer_doubleClick_Running = 0
                self._doubleClick_fired = True          # doubleClick fired
                self._timer_longClick.deinit()  # Cancels longClick timer in seconds clicks
                self.callback(Button.DOUBLE_CLICK)
            else:
                self._longClick_fired = False
                self._doubleClick_fired = False
                self._timer_longClick_Start()
        except Exception as e:
            print('In _localCallback_clickDown', e)

    def _localCallback_clickUp(self, _) -> None:
        try:
            if not self._longClick_fired:
                self._timer_longClick.deinit()
                if not self._longClick_fired and not self._doubleClick_fired:
                    self._timer_doubleClick_Start()
        except Exception as e:
            print('In _localCallback_clickUp', e)

    def buttonPressed(self, pin: Pin) -> None:
        valorPin = pin.value()
        if valorPin == self._upDown:
            # button pressed or click down
            schedule(self._localCallback_clickDown, 0)
        else:
            # button released or click up
            schedule(self._localCallback_clickUp, 0)
                
    def disable(self) -> None:
        """
        Method for disabling the button interrupts.
        The button action will no longer produce interrupts until enable() is invoked.
        Useful to avoid button interactions in critical sections of the program
        """
        self._pinButton.irq(handler=None)

    def enable(self) -> None:
        """
        Method for enabling the button interrupts.
        The button action will produce interrupts until disable() is invoked.
        Useful to allow button interactions in needed sections of the program
        """
        self._pinButton.irq(handler=self.buttonPressed, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

    def set_callback(self, callback) -> None:
        """
        Method to setup a new callback.
        This method helps to change a new button context
        """
        if not callable(callback):
            raise ButtonException("Trying to call a non callable ", f"{type(callback)}")
        self.callback = callback
