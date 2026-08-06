from micropython import const
from exceptions import MenuException

class Menu():
    '''
    menu structure needed:
        Menu Title,
        (line #, item-text, menu-link, callback, foot-text)

    menu-link = activate #menu when execute_item. 0 means no menu to activate
    callback = call callback when activate_item. None means no callback to call
                the callback is called with these arguments: active menu, active item
    foot-text =  text displayed on line 8 when item is selected

    Agregar, enabled a cada item

    '''

    def __init__(self, oled, menu: dict) -> None:
        self._menu = menu
        self._oled = oled
        self._active_level: int = 1 # Starts with menu #1
        self._active_item: int = 1   # Starts to item #1
        self._previous_item: int = 1
        self._cursor_shape: str = '-'
        self._menu_stack: list[int] = [1] # starts with menu #1
        self._max_items: int = 0 # filled whith # of items of selected menu
        self._oled_max_column: int = oled.MAX_COLUMN    # Adapted to oled size
        self._oled_max_items: int = oled.MAXLINE        # Adapted to oled size

    def _current_menu(self) -> tuple:
        '''
        Returns the tuple of menu corresponding to the active level
        '''
        return self._menu[self._active_level - 1]

    def _index_item(self):
        '''
        Returns the tuple index of current item of the menu
        1rst item is in items tuple index 0
        '''
        return self._active_item - 1

    def show(self) -> None:
        self._max_items = len(self._current_menu()[1])
        if self._max_items > self._oled_max_items - 2:  # 2 lines for head and foot text
            raise MenuException('Size of menu greater than display capacity')
        self.clear_display()
        self._oled.write_lines([(1, f'{self._current_menu()[0]:^{str(self._oled_max_column)}}')]) # Display line 1 with centered Menu name
        self._oled.write_lines([(line_text[0],' ' + line_text[1]) for line_text in self._current_menu()[1]]) # menu item tuple
    
    def select_item(self, cursor_shape: str = None) -> None:
        self._oled.delete_chars(self._previous_item + 1, 1, 1)
        self._oled.write_chars(self._active_item + 1, 1, self._cursor_shape if cursor_shape is None else cursor_shape)
        if self._current_menu()[1][self._index_item()][5]:
            self._oled.write_lines([(8, f'{self._current_menu()[1][self._index_item()][4]:^{str(self._oled_max_column)}}')]) # Display line 8 with centered Foot Text
        else:
            self._oled.write_lines([(8, 'Disabled Item !!')]) # Display line 8 with disabled message
        self._previous_item = self._active_item

    def set_cursor_shape(self, cursor_shape) -> None:
        self._cursor_shape = cursor_shape[0]
        self.select_item()

    def execute_item(self) -> None:
        if self._current_menu()[1][self._index_item()][5]:
            callback = self._current_menu()[1][self._index_item()][3]
            level = self._current_menu()[1][self._index_item()][2]
            if not callback is None:
                if not callable(callback):
                    raise MenuException(f'callback is {type(callback)} and  must be callable or None')
                callback(self._active_level, self._active_item)
            if not 0 <= level <= len(self._menu):
                raise MenuException(f'Trying to reach inexistent menu {level}')
            if level:
                self._active_level = level
                self._menu_stack.append(self._active_level)
                self._active_item = 1
                self.show()
                self.select_item()
    
    def next_item(self):
        self._active_item = self._active_item + 1 if self._active_item < self._max_items else 1
        self.select_item()

    def previous_item(self):
        self._active_item = self._active_item - 1 if self._active_item > 1 else self._max_items
        self.select_item()

    def previous_menu(self) -> None:
        if len(self._menu_stack) > 1:
            self._menu_stack.pop()
            self._active_level = self._menu_stack[-1]
            self._active_item = 1
            self.show()
            self.select_item()

    def clear_display(self):
        self._oled.clear_screen()