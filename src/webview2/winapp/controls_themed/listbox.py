from ..controls.listbox import *
from ..themes import *

LISTBOX_DARK_BG_COLOR = 0x161616
LISTBOX_DARK_BG_BRUSH = gdi32.CreateSolidBrush(LISTBOX_DARK_BG_COLOR)


########################################
# Wrapper Class
########################################
class ListBox(ListBox):

    ########################################
    #
    ########################################
    def destroy_window(self):
        if self.is_dark:
            self.parent_window.unregister_message_callback(WM_CTLCOLORLISTBOX, self._on_WM_CTLCOLORLISTBOX)
        super().destroy_window()

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

        if is_dark:
            self.parent_window.register_message_callback(WM_CTLCOLORLISTBOX, self._on_WM_CTLCOLORLISTBOX)
#            if self.has_client_edge:
#                # Replace client edge with border
#                user32.SetWindowLongA(self.hwnd, GWL_EXSTYLE, user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE) & ~WS_EX_CLIENTEDGE)
#                user32.SetWindowLongA(self.hwnd, GWL_STYLE, user32.GetWindowLongW(self.hwnd, GWL_STYLE) | WS_BORDER)
#                self.force_redraw_window()
#
##            if self.has_border or self.has_client_edge:
##                self.register_message_callback(WM_NCPAINT, self._on_WM_NCPAINT)

        else:
            self.parent_window.unregister_message_callback(WM_CTLCOLORLISTBOX, self._on_WM_CTLCOLORLISTBOX)
#            if self.has_client_edge:
#                # Replace border with client edge
#                user32.SetWindowLongA(self.hwnd, GWL_STYLE, user32.GetWindowLongW(self.hwnd, GWL_STYLE) & ~ WS_BORDER)
#                user32.SetWindowLongA(self.hwnd, GWL_EXSTYLE, user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE) | WS_EX_CLIENTEDGE)
#                self.force_redraw_window()

#            if self.has_border or self.has_client_edge:
#                self.unregister_message_callback(WM_NCPAINT, self._on_WM_NCPAINT)

#        if self.has_border:
#            self.handle_focus(is_dark)

    # #######################################
    #
    # #######################################
    def _on_WM_CTLCOLORLISTBOX(self, hwnd, wparam, lparam):
        gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
        gdi32.SetBkColor(wparam, LISTBOX_DARK_BG_COLOR)
#        gdi32.SetDCBrushColor(wparam, LISTBOX_DARK_BG_COLOR)
#        return gdi32.GetStockObject(DC_BRUSH)
        return LISTBOX_DARK_BG_BRUSH

    ########################################
    #
    ########################################
#    def _on_WM_NCPAINT(self, hwnd, wparam, lparam):
#
#        # WM_NCPAINT is also repsonsible for drawing scrollbars,
#        # so first let it do its job
#        self.old_proc(hwnd, WM_NCPAINT, wparam, lparam)
#
#        hdc = user32.GetDC(hwnd)
#
#        # Client rect would omit scrollbars, so we have to use window rect
#        rc = self.get_window_rect()
#        rc = RECT(-1, - 1, rc.right - rc.left - 1, rc.bottom - rc.top - 1)
#        user32.FrameRect(hdc, byref(rc), DARK_BORDER_BRUSH)
#        user32.ReleaseDC(hwnd, hdc)
#        return 0

#        if user32.GetFocus() == self.hwnd:
#            print('FOCUS')
