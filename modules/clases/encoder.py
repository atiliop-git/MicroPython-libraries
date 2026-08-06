"""
Class Name : Encoder
Version: 1.0
Author: Atilio Porfirio
Purpose: mechanical quadrature rotary encoder's driver
Date Creation: 24-07-2026
Last Modified: 26-07-2026
-------------------------------------------------------

Encoder is a MicroPython class to manage mechanical quadrature rotary encoders using
    GPIO of any microcontroller.
Features
    IRQ driven
License: MIT
Dependencies:
    machine
    micropython
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Hardware design:
    This class relies on low value pins activation. So the encoder's pins A and B need an
    external pull-up resistor in both pins.
    No debouncing implementation was included in its design.
    The encoder pins need to be connected to the GPIO using any electronic debouncing method,
    such as low-pass filter made by a resistor and a capacitor.
Additional Note:
The encoder's button (if it has one) is managed using the Button class, also in this library

Example:

    from encoder import Encoder

    Miencoder = Encoder(4,5,rotation)

    def rotation(direction):
        if direction == Encoder.CLOCKWISE:
            print('clockwise rotation detected')
        else:
            print('counterclockwise rotation detected')

"""

from machine import Pin
from micropython import const, schedule, alloc_emergency_exception_buf

alloc_emergency_exception_buf(100)


class Encoder:
    """
    Driver for mechanical quadrature rotary encoder

    The class detects encoder rotation using GPIO interrupts and schedules a
    callback function outside the isr context, passing the direction as an
    argument
    """

    CLOCKWISE = const(1)
    COUNTERCLOCKWISE = const(0)

    def __init__(self, pinA: int, pinB: int, callback: callable):
        """
        Creates an Encoder object
        Args:
            pinA (int):
                GPIO connected to encoder phase A

            pinB (int):
                GPIO connected to encoder phase B

            callback (callable):
                function to schedule when rotation is detected
                  Receives Encoder.CLOCKWISE or Encoder.COUNTERCLOCKWISE

        Raises:
            TypeError:
                if any parameter is invalid
        """
        if not isinstance(pinA, int) or pinA < 0:
            raise TypeError("Pin A must be a non negative integer")
        self._pinA = Pin(pinA, Pin.IN)
        if not isinstance(pinB, int) or pinB < 0:
            raise TypeError("Pin B must be a non negative number")
        self._pinB = Pin(pinB, Pin.IN)
        if not callable(callback):
            raise TypeError("callback must be a defined function")
        self.callback = callback
        self._direction = 0

        # Irq only needs to be defined on pinA
        self._pinA.irq(handler=self.encRotated, trigger=Pin.IRQ_FALLING)

    def encRotated(self, pin):
        """
        IRQ handler function

        Determines rotation direction by sampling phase B
        It schedules the user callback, outside isr context, with the direction
        """
        self._direction = Encoder.CLOCKWISE if not self._pinB.value() else Encoder.COUNTERCLOCKWISE
        schedule(self.callback, self._direction)

    # ---------------------------------------------------------------

    def disable(self):
        """
        Method for disabling the encoder interrupts.
        The encoder rotation will no longer produce interrupts until enable() is invoked.
        Useful to avoid encoder interaction in critical sections of the program
        """
        self._pinA.irq(handler=None)

    def enable(self):
        """
        Method for enabling the encoder interrupts.
        The encoder rotation will produce interrupts until disable() is invoked.
        Useful to allow encoder interaction only when is needed in any section of the program
        """
        self._pinA.irq(handler=self.encRotated, trigger=Pin.IRQ_FALLING)

    def set_callback(self, callback: callable) -> None:
        '''
        Method for setting a new user callback function.
        Modifying the callback function provides the encoder with functionality for every
        program need, whithout creating new encoder objects
        '''
        self.callback = set_callback
