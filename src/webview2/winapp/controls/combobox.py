# https://learn.microsoft.com/en-us/windows/win32/controls/combo-boxes
from ..window import *

class COMBOBOXINFO(Structure):
    def __init__(self, *args, **kwargs):
        super(COMBOBOXINFO, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", DWORD),
        ("rcItem", RECT),
        ("rcButton", RECT),
        ("stateButton", DWORD),
        ("hwndCombo", HWND),
        ("hwndItem", HWND),
        ("hwndList", HWND),
    ]


# #######################################
# Wrapper Class
# #######################################
class ComboBox(Window):

    # #######################################
    #
    # #######################################
    def __init__(
        self,
        parent_window,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        left = 0, top = 0, width = 0, height = 0,
        window_title = None,
        wrap_hwnd = None
    ):
        super().__init__(
            WC_COMBOBOX,
            parent_window = parent_window,
            style = style,
            ex_style = ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
            wrap_hwnd = wrap_hwnd
        )
