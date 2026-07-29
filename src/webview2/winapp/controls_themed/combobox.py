from ..controls.combobox import *
from ..themes import *


########################################
# Wrapper Class
########################################
class ComboBox(ComboBox): #, FocusHandler):

    ########################################
    #
    ########################################
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Find internal edit and list controls
        ci = COMBOBOXINFO()
        user32.SendMessageW(self.hwnd, CB_GETCOMBOBOXINFO, 0, byref(ci))
        self.hwnd_edit = ci.hwndItem
#        self.hwnd_listbox = ci.hwndList  # Class name is "ComboLBox"

    # #######################################
    #
    # #######################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

        uxtheme.SetWindowTheme(self.hwnd, 'DarkMode_CFD' if is_dark else 'CFD', None)

        # Update scrollbar colors
#        uxtheme.SetWindowTheme(self.hwnd_listbox, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

        if is_dark:
            self.register_message_callback(WM_CTLCOLORLISTBOX, self._on_WM_CTLCOLORLISTBOX)
            self.register_message_callback(WM_CTLCOLOREDIT, self._on_WM_CTLCOLOREDIT)
        else:
            self.unregister_message_callback(WM_CTLCOLORLISTBOX, self._on_WM_CTLCOLORLISTBOX)
            self.unregister_message_callback(WM_CTLCOLOREDIT, self._on_WM_CTLCOLOREDIT)

#        user32.InvalidateRect(self.hwnd, None, TRUE)

        # Fix some strange behavior
#        if self.hwnd_edit and self.hwnd_edit != user32.GetFocus():
#            self.send_message(CB_SETEDITSEL, 0, -1)

        #if self.has_border:
#        self.handle_focus(is_dark)

    # #######################################
    #
    # #######################################
    def _on_WM_CTLCOLORLISTBOX(self, hwnd, wparam, lparam):
        gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
        gdi32.SetBkColor(wparam, DARK_CONTROL_BG_COLOR)
        gdi32.SetDCBrushColor(wparam, DARK_CONTROL_BG_COLOR)
        return gdi32.GetStockObject(DC_BRUSH)

    # #######################################
    #
    # #######################################
    def _on_WM_CTLCOLOREDIT(self, hwnd, wparam, lparam):
        gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
        gdi32.SetBkColor(wparam, DARK_CONTROL_BG_COLOR)
        gdi32.SetDCBrushColor(wparam, DARK_CONTROL_BG_COLOR)
        return gdi32.GetStockObject(DC_BRUSH)
