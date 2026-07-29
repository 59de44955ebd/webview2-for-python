# https://learn.microsoft.com/en-us/windows/win32/controls/comboboxex-control-reference
from ..window import *

class COMBOBOXEXITEMW(Structure):
    _fields_ = [
        ("mask", UINT),
        ("iItem",  INT_PTR),
        ("pszText", LPWSTR),
        ("cchTextMax",  INT),
        ("iImage",  INT),
        ("iSelectedImage",  INT),
        ("iOverlay",  INT),
        ("iIndent",  INT),
        ("lParam", LPARAM),  # LPARAM
    ]

class NMCBEENDEDITW(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("fChanged",  BOOL),
        ("iNewSelection",  INT),
        ("szText",  WCHAR * MAX_PATH),  # WCHAR * ...
        ("iWhy",  INT),
    ]


########################################
# Wrapper Class
########################################
class ComboBoxEx(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        left = 0, top = 0, width = 0, height = 0,
        window_title = None,
        h_font = H_FONT_SHELL
    ):
        super().__init__(
            WC_COMBOBOXEX,
            parent_window = parent_window,
            style = style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
            h_font = h_font,
        )

        self.hwnd_edit = user32.SendMessageW(self.hwnd, CBEM_GETEDITCONTROL, 0, 0)
