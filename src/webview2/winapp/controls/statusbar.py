# https://learn.microsoft.com/en-us/windows/win32/controls/status-bar-reference
from ..window import *


# custom (for SB_GETBORDERS)
#class BORDERINFO(Structure):
#    _fields_ = [
#        ("horizontal", INT),
#        ("vertical", INT),
#        ("between", INT),
#    ]


########################################
# Wrapper Class
########################################
class StatusBar(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        window_title = None,
        wrap_hwnd = None,
        parts = [],
        parts_right_aligned = False,
        h_font = H_FONT_SHELL
    ):
        self.parts = parts

        num_parts = len(parts) if parts else 1
        self.parts_right_aligned = False if num_parts < 2 else parts_right_aligned

        super().__init__(
            WC_STATUSBAR,
            parent_window = parent_window,
            style = style,
            ex_style = ex_style,
            window_title = window_title,
            wrap_hwnd = wrap_hwnd,
            h_font = h_font
        )

        if num_parts > 1:
            rc = RECT()
            user32.GetWindowRect(parent_window.hwnd, byref(rc))
            w = rc.right - rc.left
            sb_parts = (INT * num_parts)()

            if self.parts_right_aligned:
                for i in range(num_parts - 1):
                    sb_parts[i] = w - sum(parts[i+1:])
            else:
                # fixed position (left aligned)
                for i in range(num_parts - 1):
                    sb_parts[i] = parts[i]

            sb_parts[num_parts - 1] = -1
            user32.SendMessageW(self.hwnd, SB_SETPARTS, num_parts, sb_parts)

        # get height of statusbar
        rc = RECT()
        user32.SendMessageW(self.hwnd, SB_GETRECT, 0, byref(rc))
        self.height = rc.bottom

    ########################################
    #
    ########################################
    def set_parts(self, parts = [], parts_right_aligned = False):
        self.parts = parts

        num_parts = len(parts) if parts else 1
        self.parts_right_aligned = False if num_parts < 2 else parts_right_aligned

        if num_parts > 1:
            rc = RECT()
            user32.GetWindowRect(self.parent_window.hwnd, byref(rc))
            w = rc.right - rc.left
            sb_parts = (INT * num_parts)()

            if self.parts_right_aligned:
                for i in range(num_parts - 1):
                    sb_parts[i] = w - sum(parts[i+1:])
            else:
                # fixed position (left aligned)
                for i in range(num_parts - 1):
                    sb_parts[i] = parts[i]

            sb_parts[num_parts - 1] = -1
            user32.SendMessageW(self.hwnd, SB_SETPARTS, num_parts, sb_parts)
        else:
            sb_parts = (INT * 1)(-1)
            res = self.send_message(SB_SETPARTS, 1, sb_parts)

    ########################################
    #
    ########################################
    def set_text(self, msg = '', part = 0):
        if part == 0:
            # We prepend 2 extra spaces to take account of rounded corners in Win 11
            user32.SendMessageW(self.hwnd, SB_SETTEXTW, 0, '  ' + msg if msg else '')
        else:
            user32.SendMessageW(self.hwnd, SB_SETTEXTW, part, msg)

    ########################################
    #
    ########################################
    def set_icon(self, hicon, part = 0):
        user32.SendMessageW(self.hwnd, SB_SETICON, part, hicon)

    ########################################
    #
    ########################################
    def right_align_parts(self, width):
        status_parts_count = len(self.parts)
        sb_parts = (INT * status_parts_count)()
        for i in range(status_parts_count - 1):
            sb_parts[i] = width - sum(self.parts[i + 1:])
        sb_parts[status_parts_count - 1] = -1
        user32.SendMessageW(self.hwnd, SB_SETPARTS, status_parts_count, sb_parts)

    ########################################
    #
    ########################################
    def update_size(self, width = 0):
        user32.SendMessageW(self.hwnd, WM_SIZE, 0, 0)
        if self.parts_right_aligned:
            self.right_align_parts(width)
