"""
Class Name : Button
Version: 1.0
Author: Atilio Porfirio
Purpose: mechanical button driver
Date Creation: 24-07-2026
Last Modified: 27-07-2026
-------------------------------------------------------

Button is a MicroPython call to manage mechanical buttons connected to a GPIO of a MC

Features:
    IRQ driven
License: MIT
Dependencies:
    machine
    micropython
    time
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Hardware design:
    The class relies on either low or high level pin activation.
    This class doesn't implement software pull-up / down thus external pull-up / down
    resistor must be used in the circuit
    No debouncing implementation was included in its design.
    The button pins need to be connected to the GPIO using any electronic debouncing method,
    such as low-pass filter made by a resistor and a capacitor.

Example:

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

"""

from micropython import const, alloc_emergency_exception_buf, schedule
from machine import Pin
from time import ticks_ms, ticks_diff

alloc_emergency_exception_buf(100)

class Button:
    '''
    Driver for mechanical button

    The class detects button click using GPIO interrupt and schedules a callback
    function outside isr context, passing short or long click as an argument
    '''

    SHORT_CLICK = const(0)
    LONG_CLICK = const(1)
    ACTIVE_HIGH = const(1)
    ACTIVE_LOW = const(0)
    
    def __init__(self, pin :int, longClick_ms :int, upDown :int, callback :callable):
        """
        Creates a Button object

        Args:
            pin (int):
                GPIO connected to the button

            longClick_ms (int):
                Duration of a long click in milliseconds
                If zero, no long click will be managed

            upDown (int):
                Level of activation.
                Button.ACTIVE_HIGH for a button that activates on high level
                Button.ACTIVE_LOW for a button that activates on low level

            callback (callable):
                Function to schedule when click is detected
                Receives SHORT_CLICK or LONG_CLICK

        Raises:
            TypeError / ValueError:
                if any parameter is invalid
        """
        if longClick_ms < 0:
            raise ValueError("longClick_ms can't be negative")
        self._longClick_ms :int = longClick_ms

        if not isinstance (pin, int) or pin < 0:
            raise TypeError("Pin must be an integer >= 0")
        self._pin = pin

        if upDown not in (Button.ACTIVE_HIGH, Button.ACTIVE_LOW):
            raise ValueError("upDown must be Button.ACTIVE_HIGH or Button.ACTIVE_LOW")
        self._upDown = upDown

        if not callable (callback):
            raise TypeError("callback must be a already defined function")
        self.callback = callback

        # Variables globales del objeto
        self._butOn = 0
        self._pinButton = Pin(self._pin, Pin.IN)
        self._pinButton.irq(handler=self.buttonPressed, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self._isrEnable = 1
        self._valorPin = 1

    def _localCallback(self, tipoClick: int) -> None:
        try:
            self.callback(tipoClick)
        except Exception as e:
            print("error: ", e)
        finally:
            self._isrEnable = 1

    def buttonPressed(self, pin):
        '''
        IRQ handler function

        Determines long or short click duration
        It shedules the user callback, outside the ISR context, with the type of click 
        '''
        if not self._isrEnable:
            return
        self._isrEnable = 0
        self._valorPin = self._pinButton.value()
        if self._valorPin == self._upDown:
            self._butOn = ticks_ms()
            self._isrEnable = 1
        else:
            if not self._longClick_ms:
                schedule(self._localCallback, Button.SHORT_CLICK)
            else:
                if ticks_diff(ticks_ms(), self._butOn) > self._longClick_ms:
                    schedule(self._localCallback, Button.LONG_CLICK)
                else:
                    schedule(self._localCallback, Button.SHORT_CLICK)

    def disable(self):
        '''
        Method for disabling the button interrupts.
        The button action will no longer produce interrupts until enable() is invoked.
        Useful to avoid button interactions in critical sections of the program
        '''
        self._pinButton.irq(handler=None)

    def enable(self):
        """
        Method for enabling the button interrupts.
        The button action will produce interrupts until disable() is invoked.
        Useful to allow button interactions in needed sections of the program
        """
        self._pinButton.irq(handler=self.buttonPressed, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
