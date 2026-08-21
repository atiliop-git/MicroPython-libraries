"""
Class Name : Menu
Version: 1.0
Author: Atilio Porfirio
Purpose: Menu driver for OLED display
Date Creation: 01-08-2026
Last Modified: 06-08-2026
-------------------------------------------------------

Menu is a MicroPython class to manage menu structures for OLED displays

Features:
    Manages menu structures for OLED displays with no limit on the number of menus or submenus
    There is a limit in the amount of Items of a menu, which is determined by the OLED display size.
    The class will raise an exception if the menu structure exceeds the display capacity.
License: MIT
Dependencies:
    exceptions
Tested on:
    RaspBerry Py Pico 2040 Zero
    Wokwi web simulator
Menu design example:
menu = (
        ('Electr. Charge',   # menu #1
            (
                (2,'Setup Values', 2, None, 'Click to enter', True),
                (3,'Run/Stop', 0, muestra_algo, 'Run/Stop charge', True)
            ),
        ),
        ('Set Parameters',  # menu #2
            (
                (2,'Set Current', 0, None, 'Current value', True),
                (3,'Set Power', 0, None, 'Power value', True),
                (4,'Set Resistance', 0, None, 'Resistance value', True),
                (5,'Set min Voltage', 0, None, 'Low Volt Value', True),
                (6,'Set time limit', 0, None, 'Run Time Limit', True),
                (7,'Return', 1, None, 'Main Menu', True),
            )
        )
    )

    Menu Title: the first element of the menu, that is displayed on line 1 of the
        OLED display when the menu is selected
    Items: the second element of the menu, that is a tuple of items, each item is a tuple with the following elements:
        line: line number of the item on the OLED display, starting from 2 to 7 (line 1 is reserved for the menu title)
        text: text displayed on the line of the item
        menu-link: menu to activate when item is selected. 0 means no menu to activate
        callback: callback function to call when item is selected. None means no callback to call
                the callback is called with these arguments: active menu, active item
        Enabled: boolean value to indicate if the item is enabled or disabled.
            If disabled, the item will be displayed with a message "Disabled Item !!" on line 8
            of the OLED display when selected. No action will be taken when the item is selected,
            even if a callback is defined.

Example of usage:

    from menu import Menu
    from oled1306I2c import Oled1306I2c
    from encoder import Encoder
    from button import Button

 def muestra_algo(menu, item):
 print(f'hizo click en menu {menu} item {item}')
 menu = (
         ('Electr. Charge',   # menu #1
             (
                 (2,'Setup Values', 2, None, 'Click to enter', True),
                 (3,'Run/Stop', 0, muestra_algo, 'Run/Stop charge', True)
             ),
         ),
         (   # menu #2
             'Set Parameters',
             (
                 (2,'Set Current', 0, None, 'Current value', True),
                 (3,'Set Power', 0, None, 'Power value', True),
                 (4,'Set Resistance', 0, None, 'Resistance value', True),
                 (5,'Set min Voltage', 0, None, 'Low Volt Value', True),
                 (6,'Set time limit', 0, None, 'Run Time Limit', True),
                 (7,'Return', 1, None, 'Main Menu', True),
             )
             )
 )

 def set_cursor_position(direction):
     if direction == Encoder.CLOCKWISE:
         Main_menu.next_item()
     else:
         Main_menu.previous_item()

 def execute_item(long_short_click: int) -> None:
     if long_short_click == Button.SHORT_CLICK:
         Main_menu.execute_item()
     else:
         Main_menu.previous_menu()

 callback_encoder: callable = set_cursor_position
 callback_button: callable = execute_item

 e = Encoder(4,5,callback_encoder)
 b = Button(6, 400, 0, callback_button)
 oled = Oled1306I2c(sda_pin = 0, scl_pin = 1)
 Main_menu = Menu (oled, menu)

 Main_menu.show()
 Main_menu.select_item()

 while True:
     pass

"""

from exceptions import MenuException


class Menu:
    """
    This class manages menu structures for OLED displays
    The menu structure is dependent on the OLED display size, and the class will raise an exception
    if the menu structure exceeds the display capacity.
    """

    def __init__(self, oled, menu: dict) -> None:
        """
        Initializes the Menu class.
        Receive an oled object and a menu as parameter
        the _oled_max_items and _oled_max_columns are set according to the oled object passed as parameter
        """
        self._menu = menu
        self._oled = oled
        self._active_level: int = 1  # Starts with menu #1
        self._active_item: int = 1  # Starts to item #1
        self._previous_item: int = 1
        self._cursor_shape: str = "-"
        self._menu_stack: list[int] = [1]  # starts with menu #1
        self._max_items: int = 0  # filled with # of items of selected menu
        self._oled_max_column: int = oled.MAX_COLUMN  # Adapted to oled size
        self._oled_max_items: int = oled.MAXLINE  # Adapted to oled size

    def _current_menu(self) -> tuple:
        """
        Returns the tuple of menu corresponding to the active level
        """
        return self._menu[self._active_level - 1]

    def _index_item(self):
        """
        Returns the tuple index of current item of the menu
        1rst item is in items tuple index 0
        """
        return self._active_item - 1

    def show(self) -> None:
        """
        Displays the current menu on the OLED display
        """
        self._max_items = len(self._current_menu()[1])
        if self._max_items > self._oled_max_items - 2:  # 2 lines for head and foot text
            raise MenuException("Size of menu greater than display capacity")
        self.clear_display()
        self._oled.write_lines([(1, f"{self._current_menu()[0]:^{str(self._oled_max_column)}}")])  # Display line 1 with centered Menu name
        self._oled.write_lines([(line_text[0], " " + line_text[1]) for line_text in self._current_menu()[1]])  # menu item tuple

    def select_item(self, cursor_shape: str = None) -> None:
        """
        Selects the current item and displays a character in the first column of the line of the item
        to indicate that it is selected
        Displays the foot text of the item on line 8 of the OLED display, if the item is enabled
        If the item is disabled, displays a message "Disabled Item !!" on line 8
        """
        self._oled.delete_chars(self._previous_item + 1, 1, 1)
        self._oled.write_chars(self._active_item + 1, 1, self._cursor_shape if cursor_shape is None else cursor_shape)
        if self._current_menu()[1][self._index_item()][5]:
            self._oled.write_lines([(8, f"{self._current_menu()[1][self._index_item()][4]:^{str(self._oled_max_column)}}")])  # Display line 8 with centered Foot Text
        else:
            self._oled.write_lines([(8, "Disabled Item !!")])  # Display line 8 with disabled message
        self._previous_item = self._active_item

    def set_cursor_shape(self, cursor_shape) -> None:
        """
        Change the cursor shape to the one passed as parameter and select the current item with the new cursor shape
        """
        self._cursor_shape = cursor_shape[0]
        self.select_item()

    def execute_item(self) -> None:
        """
        Executes the callback or changes to the menu linked to the current item
        Callback is priority. If exists, calls it and ignore menu change
        If the item is disabled, no action is taken
        add the current menu to the menu stack and set the active level to the menu linked to the item
        Checks if the menu linked and the callback is valid, if not raises an exception
        """
        if self._current_menu()[1][self._index_item()][5]:
            callback = self._current_menu()[1][self._index_item()][3]
            level = self._current_menu()[1][self._index_item()][2]
            input_item = self._current_menu()[1][self._index_item()][6]
            if not callback is None:
                if not callable(callback):
                    raise MenuException(f"callback: {callback.__name__} is of type {type(callback)} and  must be callable or None")
                else:
                    # callback available. Calls it
                    callback(self._active_level, self._active_item, input_item)
            else:
                # No callback. Tries to jump to other menu
                if not 0 <= level <= len(self._menu):
                    raise MenuException(f"Trying to reach inexistent menu {level}")
                if level:
                    self._active_level = level
                    self._menu_stack.append(self._active_level)
                    self._active_item = 1
                    self.show()
                    self.select_item()

    def next_item(self):
        """
        Moves the cursor to the next item in the menu
        """
        self._active_item = self._active_item + 1 if self._active_item < self._max_items else 1
        self.select_item()

    def previous_item(self):
        """
        Moves the cursor to the previous item in the menu
        """
        self._active_item = self._active_item - 1 if self._active_item > 1 else self._max_items
        self.select_item()

    def previous_menu(self) -> None:
        """
        Goes back to the previous menu, and selects the first item of that menu
        If the current menu is the first menu, no action is taken
        """
        if len(self._menu_stack) > 1:
            self._menu_stack.pop()
            self._active_level = self._menu_stack[-1]
            self._active_item = 1
            self.show()
            self.select_item()

    def clear_display(self):
        """
        Clears the OLED display
        """
        self._oled.clear_screen()
