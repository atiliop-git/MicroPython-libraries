# <center>MicroPython Library</center>

## Key Features:
These library modules are designed using POO to facilitate the management of common devices in electronics projects using microcontrollers GPIO, programmed in MicroPython.
Its design relies on a compact ISR code, and external user defined callbacks to handle the IRQ events, relieving developers of the tedious task of dealing with GPIO interruptions, and the need of thinking program logic to manage the devices like oled displays, rotary encoders and buttons.
The library also has a couple of modules (menu and data_input) with classes to manage menus and data inputs, using oled displays and encoders and buttons.

## Electronic design Requirements
### Low-Pass filters and Pull-Up/Down resistors
While these libraries were created with simplicity and efficiency in mind, they do not include code to prevent bouncing in buttons, encoders, and other devices susceptible to this problem. It is well known that much better solutions exist for these problems using electronic components, such as low-pass filters and schmitt-triggers to prevent bounce, for example.
Another design concept is the decision to base the function of the controllers on the use of I2C objects instantiated by the users, to adapt I2C pins to the module used in the project. So pull-up/pull-down needed in the I2C pins can be defined in I2C Pin instantiation, or using external resistors on the GPIO pins, to give projects greater design flexibility.

## Project Structure
This library is made by modules. Each module contains the classes needed to drive a single device.
The documentation of each class is written in the REAME.md file in classes directory
