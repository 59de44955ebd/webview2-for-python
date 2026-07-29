from ..controls.statusbar import *
from ..themes import *


########################################
# Wrapper Class
########################################
class StatusBar(StatusBar):

    ########################################
    #
    ########################################
    def __init__(
        self,
        *args,
        bg_brush_dark = DARK_BG_BRUSH,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.bg_brush_dark = bg_brush_dark

#        if self.parent_window.is_dark:
#            self.apply_theme(True)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

        if is_dark:
            self.register_message_callback(WM_PAINT, self._on_WM_PAINT)
            self.register_message_callback(WM_ERASEBKGND, self._on_WM_ERASEBKGND)
        else:
            self.unregister_message_callback(WM_PAINT, self._on_WM_PAINT)
            self.unregister_message_callback(WM_ERASEBKGND, self._on_WM_ERASEBKGND)

#        user32.RedrawWindow(self.hwnd, 0, 0, RDW_FRAME | RDW_ERASE | RDW_INVALIDATE) # | RDW_ALLCHILDREN)

    ########################################
    #
    ########################################
    def _on_WM_ERASEBKGND(self, hwnd, wparam, lparam):
        return 0

    ########################################
    #
    ########################################
    def _on_WM_PAINT(self, hwnd, wparam, lparam):
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(self.hwnd, byref(ps))

#        ps.rcPaint.right -= 1
        user32.FillRect(hdc, byref(ps.rcPaint), self.bg_brush_dark)

        user32.FillRect(hdc, byref(RECT(ps.rcPaint.left, ps.rcPaint.top, ps.rcPaint.right, ps.rcPaint.top + 1)), DARK_SEPARATOR_BRUSH)

        gdi32.SelectObject(hdc, self.h_font)
        gdi32.SetBkMode(hdc, TRANSPARENT)
        gdi32.SetTextColor(hdc, DARK_TEXT_COLOR)

        rc_part = RECT()

        for i in range(len(self.parts) + 1):
            user32.SendMessageW(self.hwnd, SB_GETRECT, i, byref(rc_part))
            if ps.rcPaint.left >= rc_part.right or ps.rcPaint.right < rc_part.left:
                continue

            # Draw text
            text_len = user32.SendMessageW(self.hwnd, SB_GETTEXTLENGTHW, i, 0) + 1
            buf = create_unicode_buffer(text_len)
            user32.SendMessageW(self.hwnd, SB_GETTEXTW, i, buf)
            user32.DrawTextW(hdc, buf.value, text_len,
                    byref(RECT(rc_part.left + 2, rc_part.top + 1, rc_part.right, rc_part.bottom - 1)),
                    DT_SINGLELINE | DT_VCENTER | DT_LEFT)

            # Draw separator
            if i < len(self.parts) - 1:
                user32.FillRect(hdc, byref(RECT(rc_part.right - 1, rc_part.top + 1, rc_part.right, rc_part.bottom - 3)),
                        DARK_SEPARATOR_BRUSH)

        user32.EndPaint(self.hwnd, byref(ps))
        return 0
