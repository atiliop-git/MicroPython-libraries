"""
Class Name : Beep
Version: 1.0
Author: Atilio Porfirio
Purpose: Handles beeps in a non-blocking way using a Timer
Date Creation: 02-10-2026
Last Modified: 02-10-2026
-------------------------------------------------------

Beep is a MicroPython class to manage beeps using active buzzers connected to a GPIO of a MC

Features:
    Timer driven
License: MIT
Dependencies:
    machine
    micropython
Tested on:
    RaspBerry Py Pico 2040 Zero
Hardware/Software design:
    The class relies on a Timer that will toggle the buzzer pin state to generate beeps.
    Once the beep method is called, the buzzer will beep for the specified duration and number
    of times without blocking the main program flow.

Example:

    from beep import Beep

    MyBuzzer = Beep(pin = (Pin(4, Pin.OUT)), active=Beep.ACTIVE_HIGH)

    # buzzer GPIO pin = 4
    # buzzer activates on high value

    MyBuzzer.beep(last_ms=100, times=3)

    # Beep duration in ms = 100 ms
    # Number of beeps = 3

    """
from machine import Pin, Timer # type: ignore
from micropython import const, alloc_emergency_exception_buf, schedule # type: ignore
try:
    from typing import Callable
except ImportError:
    pass

alloc_emergency_exception_buf(200)

class Beep():

    ACTIVE_LOW: int = const(0)
    ACTIVE_HIGH: int = const(1)

    def __init__(self, pin: Pin, active: int = ACTIVE_LOW) -> None:
        """Instantiate a buzzer object in pin, and set it off

        Args:
            pin (Pin): Pin in what the active buzzer is connected
            active (int, optional): Sets if the buzzer actives on high or low value.
            Defaults to ACTIVE_LOW.

        Raises:
            TypeError: if arguments don't match the expected type
            ValueError: checks the range of the arguments
        
        """
        if not isinstance(pin, Pin):
            raise TypeError("pin must be a Pin object")
        self.buzzer: Pin = pin
        
        if not isinstance(active, int):
            raise TypeError("active must be an integer")
        if not (active == self.ACTIVE_LOW or active == self.ACTIVE_HIGH):
            raise ValueError("active must be either ACTIVE_LOW or ACTIVE_HIGH")
        self.active: int = active
        # sets instance variables
        self.timerBuzzer: Timer = Timer(-1)
        self._times: int = 0
        self.buzzerState: int = 0
        # starts with buzzer off
        self.beepOff()

    def beep(self, last_ms: int, times: int = 1) -> None:
        """Generates beeps on the buzzer

        Args:
            last_ms (int): Duration of each beep
            times (int, optional): Amount of beeps. Defaults to 1.

        Raises:
            TypeError: Checks that types of arguments are as expected
            ValueError: Checks the limits of the arguments
        """
        if not isinstance(last_ms, int):
            raise TypeError("last_ms must be an integer")
        if not (10 <= last_ms <= 2000):
            raise ValueError("last_ms must be between 10 and 2000")
        self.last_ms: int = last_ms

        if not isinstance(times, int):
            raise TypeError("times must be an integer")
        if not (1 <= times <= 10):
            raise ValueError("times must be between 1 and 10")
        # sets the number of times to beep, multiplied by 2 because each beep consists of an on and off state
        self._times = times * 2
        self.timerBuzzer.init(period=self.last_ms, mode=Timer.PERIODIC, callback=self._localCallback)

    def _localCallback(self, timer: Timer) -> None:
        """
        ISR callback for Timer
        """
        schedule(self._toggle_buzzer, 0)

    def _toggle_buzzer(self, _) -> None:
        """
        Toggles buzzer state to on and off. As self.times is odd (2 times times), the buzzer ends in off state
        because allways starts in on state because self.buzzerState is initialized to 0 (off)
        """
        if self.buzzerState == 0:
            self.beepOn()
        else:
            self.beepOff()
        self._times -= 1
        if self._times == 0:
            self.timerBuzzer.deinit()
            self.buzzerState = 0

    def beepOn(self) -> None:
        if self.active == self.ACTIVE_LOW:
            self.buzzer.value(0)
        else:
            self.buzzer.value(1)
        self.buzzerState = 1

    def beepOff(self) -> None:
        if self.active == self.ACTIVE_LOW:
            self.buzzer.value(1)
        else:
            self.buzzer.value(0)
        self.buzzerState = 0
    