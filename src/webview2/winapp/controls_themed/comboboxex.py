from ..controls.comboboxex import *
from .combobox import *
from ..themes import *

ICON_SIZE = 16

DARK_COMBOBOX_BORDER_BRUSH = gdi32.CreateSolidBrush(0x808080)  # DARK_BORDER_BRUSH
DARK_COMBOBOX_BORDER_HIGHLIGHT_BRUSH = gdi32.CreateSolidBrush(0xD47800)


########################################
# Wrapper Class
########################################
class ComboBoxEx(ComboBoxEx):

    ########################################
    #
    ########################################
    def __init__(self, parent_window, *args, **kwargs):

        super().__init__(parent_window, *args, **kwargs)

        self._has_focus = False

        # Find internal combobox control
        self.hwnd_combobox = user32.SendMessageW(self.hwnd, CBEM_GETCOMBOCONTROL, 0, 0)
        self.combobox = Window(wrap_hwnd = self.hwnd_combobox)

        ci = COMBOBOXINFO()
        user32.SendMessageW(self.hwnd_combobox, CB_GETCOMBOBOXINFO, 0, byref(ci))
        self.hwnd_listbox = ci.hwndList  # Class name is "ComboLBox"

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

        uxtheme.SetWindowTheme(self.hwnd_combobox, 'DarkMode_CFD' if is_dark else 'CFD', None)

        # Update scrollbar colors
        uxtheme.SetWindowTheme(self.hwnd_listbox, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

        if is_dark:
            self.register_message_callback(WM_DRAWITEM, self._on_WM_DRAWITEM)
            self.register_message_callback(WM_ERASEBKGND, self._on_WM_ERASEBKGND)
            self.register_message_callback(WM_CTLCOLOREDIT, self._on_WM_CTLCOLOREDIT)

            self.combobox.register_message_callback(WM_SIZE, self._on_WM_SIZE)
            self.combobox.register_message_callback(WM_COMMAND, self._on_WM_COMMAND)

            self.combobox.register_message_callback(WM_ERASEBKGND, self._on_WM_ERASEBKGND)

            rc = RECT()
            user32.GetClientRect(self.hwnd_combobox, byref(rc))
            user32.SetWindowRgn(self.hwnd_combobox, gdi32.CreateRectRgn(1, 1, rc.right - 1, rc.bottom - 1), FALSE)

        else:
            self.unregister_message_callback(WM_DRAWITEM, self._on_WM_DRAWITEM)
            self.unregister_message_callback(WM_ERASEBKGND, self._on_WM_ERASEBKGND)
            self.unregister_message_callback(WM_CTLCOLOREDIT, self._on_WM_CTLCOLOREDIT)

            self.combobox.unregister_message_callback(WM_SIZE, self._on_WM_SIZE)
            self.combobox.register_message_callback(WM_COMMAND, self._on_WM_COMMAND)

            user32.SetWindowRgn(self.hwnd_combobox, None, FALSE)

        user32.SetWindowPos(self.hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)

    ########################################
    #
    ########################################
    def _on_WM_COMMAND(self, hwnd, wparam, lparam):
        if HIWORD(wparam) == EN_SETFOCUS:
            self._has_focus = True
            user32.InvalidateRect(self.hwnd, None, TRUE)
        elif HIWORD(wparam) == EN_KILLFOCUS:
            self._has_focus = False
            user32.InvalidateRect(self.hwnd, None, TRUE)

    ########################################
    #
    ########################################
    def _on_WM_SIZE(self, hwnd, wparam, lparam):
        width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
        user32.SetWindowRgn(hwnd, gdi32.CreateRectRgn(1, 1, width - 1, height - 1), TRUE)

    ########################################
    #
    ########################################
    def _on_WM_CTLCOLOREDIT(self, hwnd, wparam, lparam):
        gdi32.SetTextColor(wparam, DARK_TEXT_COLOR)
        gdi32.SetBkColor(wparam, DARK_CONTROL_BG_COLOR)
        gdi32.SetDCBrushColor(wparam, DARK_CONTROL_BG_COLOR)
        return gdi32.GetStockObject(DC_BRUSH)

    ########################################
    # Draws popup list
    ########################################
    def _on_WM_DRAWITEM(self, hwnd, wparam, lparam):
        di = cast(lparam, POINTER(DRAWITEMSTRUCT)).contents

        if di.itemState & ODS_COMBOBOXEDIT:
            return

#        rc = RECT()
#        user32.GetClientRect(self.hwnd, byref(rc))
#        rc.top -= 2
#        user32.FillRect(di.hDC, byref(rc), gdi32.GetStockObject(BLACK_BRUSH))  #DARK_CONTROL_BG_BRUSH)

        buf = create_unicode_buffer(MAX_PATH)

        cbei = COMBOBOXEXITEMW()
        cbei.mask = CBEIF_TEXT | CBEIF_IMAGE
        cbei.cchTextMax = MAX_PATH
        cbei.pszText = cast(buf, LPWSTR)
        cbei.iItem = di.itemID

        user32.SendMessageW(self.hwnd, CBEM_GETITEMW, 0, byref(cbei))

        gdi32.SetTextColor(di.hDC, DARK_TEXT_COLOR)

#        gdi32.SetBkColor(di.hDC, HIGHLIGHT_COLOR if di.itemState & ODS_SELECTED else DARK_CONTROL_BG_COLOR)

        # Calculate the vertical and horizontal position.
        tm = TEXTMETRICW()
        gdi32.GetTextMetricsW(di.hDC, byref(tm))
        y = (di.rcItem.bottom + di.rcItem.top - tm.tmHeight) // 2
        x = LOWORD(user32.GetDialogBaseUnits()) // 4

        # 6 = ETO_CLIPPED | ETO_OPAQUE
        gdi32.ExtTextOutW(di.hDC, ICON_SIZE + 2 * x, y, 6, byref(di.rcItem), cbei.pszText, len(buf.value), None)

        h_imagelist = user32.SendMessageW(self.hwnd, CBEM_GETIMAGELIST, 0, 0)
        if h_imagelist and cbei.iImage >= 0:
            comctl32.ImageList_Draw(h_imagelist, cbei.iImage, di.hDC, x, y, ILD_IMAGE)

        # If an application processes this message, it should return TRUE.
        return TRUE

    ########################################
    #
    ########################################
    def _on_WM_ERASEBKGND(self, hwnd, wparam, lparam):
        rc = RECT()
        user32.GetClientRect(self.hwnd, byref(rc))
#        user32.FillRect(wparam, byref(rc), DARK_CONTROL_BG_BRUSH)
        user32.FrameRect(wparam, byref(rc), DARK_COMBOBOX_BORDER_HIGHLIGHT_BRUSH if self._has_focus else DARK_COMBOBOX_BORDER_BRUSH)
        return 1
