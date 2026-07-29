from ..controls.edit import *
from ..themes import *


########################################
# Wrapper Class
########################################
class Edit(Edit): #, FocusHandler):

    ########################################
    #
    ########################################
    def __init__(
        self,
        *args,
        bg_color_dark = DARK_CONTROL_BG_COLOR,
        text_color_dark = DARK_TEXT_COLOR,
        **kwargs
    ):
        self.bg_color_dark = bg_color_dark
        self.text_color_dark = text_color_dark

        super().__init__(*args, **kwargs)

    ########################################
    #
    ########################################
    def destroy_window(self):
        if self.is_dark:
            self.parent_window.unregister_message_callback(WM_CTLCOLOREDIT, self._on_WM_CTLCOLOREDIT)
        super().destroy_window()

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)
        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

        if is_dark:
#            uxtheme.SetWindowTheme(self.hwnd, '', '')

            # Replace client edge with border
            ex_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
            if ex_style & WS_EX_CLIENTEDGE:
                style = user32.GetWindowLongW(self.hwnd, GWL_STYLE)
                user32.SetWindowLongA(self.hwnd, GWL_STYLE, style | WS_BORDER)
                user32.SetWindowLongA(self.hwnd, GWL_EXSTYLE, ex_style & ~WS_EX_CLIENTEDGE)
                user32.SetWindowPos(self.hwnd, 0, 0,0, 0,0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
            self.parent_window.register_message_callback(WM_CTLCOLOREDIT, self._on_WM_CTLCOLOREDIT)

        else:
            # Replace border with client edge
            style = user32.GetWindowLongW(self.hwnd, GWL_STYLE)
            if style & WS_BORDER:
                ex_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
                user32.SetWindowLongA(self.hwnd, GWL_EXSTYLE, ex_style | WS_EX_CLIENTEDGE)
                user32.SetWindowLongA(self.hwnd, GWL_STYLE, style & ~WS_BORDER)
                user32.SetWindowPos(self.hwnd, 0, 0,0, 0,0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
            self.parent_window.unregister_message_callback(WM_CTLCOLOREDIT, self._on_WM_CTLCOLOREDIT)

#        if self.has_border:
#            self.handle_focus(is_dark)

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLOREDIT(self, hwnd, wparam, lparam):
        if lparam == self.hwnd:
            gdi32.SetTextColor(wparam, self.text_color_dark)
            gdi32.SetBkColor(wparam, self.bg_color_dark)
            gdi32.SetDCBrushColor(wparam, self.bg_color_dark)
            return gdi32.GetStockObject(DC_BRUSH)



#    ########################################
#    #
#    ########################################
#    def _on_WM_SETFOCUS(self, hwnd, wparam, lparam):
#        print('_on_WM_SETFOCUS')
#        hdc = user32.GetWindowDC(hwnd)
#        rc = self.get_window_rect()
#        rc = RECT(0, 0, rc.right - rc.left, rc.bottom - rc.top)
#        user32.FrameRect(hdc, byref(rc), HIGHLIGHT_BRUSH)
#        user32.ReleaseDC(hwnd, hdc)
#        return 1
#
#    ########################################
#    #
#    ########################################
#    def _on_WM_KILLFOCUS(self, hwnd, wparam, lparam):
#        print('_on_WM_KILLFOCUS ')
#        hdc = user32.GetWindowDC(hwnd)
#        rc = self.get_window_rect()
#        rc = RECT(0, 0, rc.right - rc.left, rc.bottom - rc.top)
#        user32.FrameRect(hdc, byref(rc), DARK_BORDER_BRUSH)
#        user32.ReleaseDC(hwnd, hdc)
#        return 1
#
#    ########################################
#    #
#    ########################################
#    def _on_WM_NCPAINT(self, hwnd, wparam, lparam):
#        hdc = user32.GetWindowDC(hwnd)
#        rc = self.get_window_rect()
#        rc = RECT(0, 0, rc.right - rc.left, rc.bottom - rc.top)
##        if self.has_border:
##            user32.InflateRect(byref(rc), 1, 1)
#        user32.FrameRect(hdc, byref(rc), HIGHLIGHT_BRUSH)
##            user32.InflateRect(byref(rc), -1, -1)
##        user32.FrameRect(hdc, byref(rc), DARK_CONTROL_BG_BRUSH)
##        user32.FillRect(hdc, byref(rc), DARK_CONTROL_BG_BRUSH)
#        user32.ReleaseDC(hwnd, hdc)
#        return 0