# https://learn.microsoft.com/en-us/windows/win32/controls/list-boxes
from ..window import *

class DRAGLISTINFO(Structure):
    _fields_ = [
        ('uNotification', UINT),
        ('hWnd', HWND),
        ('ptCursor', POINT),
    ]


########################################
# Wrapper Class
########################################
class ListBox(Window):

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
        wrap_hwnd = None,
        h_font = H_FONT_SHELL,
    ):
        super().__init__(
            WC_LISTBOX,
            parent_window = parent_window,
            style = style,
            ex_style = ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
            wrap_hwnd = wrap_hwnd,
            h_font = h_font,
        )

#        self.has_border = (style & WS_BORDER)
        self.has_client_edge = (ex_style & WS_EX_CLIENTEDGE)

    ########################################
    #
    ########################################
    def add_string(self, s, data=None):
        idx = user32.SendMessageW(self.hwnd, LB_ADDSTRING, 0, s)
        if data is not None:
            user32.SendMessageW(self.hwnd, LB_SETITEMDATA, idx, data)
        return idx

#    ########################################
#    #
#    ########################################
#    def set_item_data(self, idx, data):
#        user32.SendMessageW(self.hwnd, LB_SETITEMDATA, idx, data)
#
#    ########################################
#    #
#    ########################################
#    def rename_item(self, idx, new_name):
#        data = user32.SendMessageW(self.hwnd, LB_GETITEMDATA, idx, 0)
#        user32.SendMessageW(self.hwnd, LB_DELETESTRING, idx, 0)
#        idx = user32.SendMessageW(self.hwnd, LB_ADDSTRING, 0, new_name)
#        user32.SendMessageW(self.hwnd, LB_SETITEMDATA, idx, data)
#
#    ########################################
#    #
#    ########################################
#    def find_item_by_data(self, data):
#        cnt = user32.SendMessageW(self.hwnd, LB_GETCOUNT, 0, 0)
#        for idx in range(cnt):
#            if user32.SendMessageW(self.hwnd, LB_GETITEMDATA, idx, 0) == data:
#                return idx
