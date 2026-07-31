# <center>MicroPython Library</center>

## Characteristics:
These library modules are designed using POO to facilitate the management of common devices in electronics projects using microcontrollers GPIO, programmed in MicroPython.
It's design relays on a compact isr code, and externall user defined callbacks to handle the irq events.

## Requirements
### Low-Pass filters and Pull-Up/Down resistors
While these libraries were created with simplicity and efficiency in mind, they do not include code to prevent bouncing in buttons, encoders, and other devices susceptible to this problem. It is well known that much better solutions exist for these problems using electronic components, such as low-pass filters to prevent bounce, for example.
Another design concept is the decision to base the function of the controllers on the use of external pull-up/pull-down resistors on the GPIO pins, to give projects greater design flexibility.

## Project Structure
This library is made by modules. Each module contents the classes needed to drive a single device.
The documentation of each class is written in the module file.  
The main characteristics of the modules of this library, are shown below

## Clases

### Button
Class to manage event short and long clicks on buttons connected to a GPIO microcontrollers
#### Main features
>* Irq driven
>* Trigger on high or low value
>* Normal Close or Normal Open buttons
>* Detect short or long clicks (Long click duration especified in the instanciation)
>* Uses an external (outside ISR context) user callback
>* No limit for the external user callback

### Encoder
Class to manage mechanical quadrature rotary encoders connected to GPIO microcontrollers
#### Main features
>* Irq driven
>* Detects clockwise and counterclockwise turn, and passes the direction to an external (outside the ISR context) user callback
>* No limit for the external user callback

## Examples
### Button
```Python
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
```
### Encoder
``` Python
    from encoder import Encoder

    Miencoder = Encoder(4,5,rotation)

    def rotation(direction):
        if direction == Encoder.CLOCKWISE:
            print('clockwise rotation detected')
        else:
            print('counterclockwise rotation detected')

```
## Hardware Design
Below is shown an example of how to connect a button.
Low-Pass filter and Pull-up is needed
![Button](image.png)

This is an example of an encoder connection
There is Low-Pass filters and Pull-Up resistors in each GPIO pins
![Encoder](image-1.png)

## Compatibility
This library's modules were tested in a real hardware on a RP2040 Zero , but no changes are needed to run in other `MicroPython based microcontrollers`

## Limitations
* No code for debouncing are implemented
* No embedded GPIO Pull-Up/Down are implemented in GPIO pins
* Designed only for MicroPython bases microcontrollers

## Installation
Copy the .py file of the module(s) needed to the /lib folder of the microcontroller file system
See the examples above

## Upcoming Improvements
There are modules to be added to this library, such as:
* Oled display modules
* Ina219 Volt and current sensor module
* ZMPT101B voltage sensor module
* Menu driver module

## License

MIT license