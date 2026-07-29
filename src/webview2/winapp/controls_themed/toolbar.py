from ..controls.toolbar import *
from ..themes import *

DARK_TOOLBAR_BUTTON_CHECKED_BG_COLOR = 0x383838
DARK_TOOLBAR_BUTTON_CHECKED_BG_BRUSH = gdi32.CreateSolidBrush(DARK_TOOLBAR_BUTTON_CHECKED_BG_COLOR)

DARK_TOOLBAR_BUTTON_CHECKED_BORDER_COLOR = 0x646464

DARK_TOOLBAR_BUTTON_ROLLOVER_BG_COLOR = 0x454545
DARK_TOOLBAR_BUTTON_ROLLOVER_BG_BRUSH = gdi32.CreateSolidBrush(DARK_TOOLBAR_BUTTON_ROLLOVER_BG_COLOR)

DARK_TOOLBAR_BUTTON_ROLLOVER_BORDER_COLOR = 0x9b9b9b

DARK_TOOLBAR_BORDER_BRUSH = DARK_SEPARATOR_BRUSH #gdi32.CreateSolidBrush(0x424242)  #DARK_BORDER_BRUSH

DARK_TOOLBAR_BUTTON_ROLLOVER_BORDER_PEN = gdi32.CreatePen(PS_SOLID, 1, DARK_TOOLBAR_BUTTON_ROLLOVER_BORDER_COLOR)
DARK_TOOLBAR_BUTTON_CHECKED_BORDER_PEN = gdi32.CreatePen(PS_SOLID, 1, DARK_TOOLBAR_BUTTON_CHECKED_BORDER_COLOR)


########################################
# Wrapper Class
########################################
class ToolBar(ToolBar):

    ########################################
    #
    ########################################
    def __init__(
        self,
        *args,

        h_bitmap_dark = None,
        h_imagelist_dark = None,
        h_imagelist_disabled_dark = None,

        bg_brush_dark = DARK_BG_BRUSH,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.h_bitmap_dark = h_bitmap_dark
        self.h_imagelist_dark = h_imagelist_dark
        self.h_imagelist_disabled_dark = h_imagelist_disabled_dark
        self.bg_brush_dark = bg_brush_dark

        self._i = 0

        ########################################
        #
        ########################################
#        def _on_WM_ERASEBKGND(hwnd, wparam, lparam):
#            return 0

        #self.register_message_callback(WM_ERASEBKGND, _on_WM_ERASEBKGND)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        super().apply_theme(is_dark)

#        if is_dark:
#            uxtheme.SetWindowTheme(self.hwnd, '', '')
#        else:
#            uxtheme.SetWindowTheme(self.hwnd, 'Explorer', None)
#
#        self.set_font()

        if self.h_bitmap_dark:
            rb = TBREPLACEBITMAP()
            if is_dark:
                rb.nIDOld = self.h_bitmap
                rb.nIDNew = self.h_bitmap_dark
            else:
                rb.nIDOld = self.h_bitmap_dark
                rb.nIDNew = self.h_bitmap
            rb.nButtons = self.num_images
            image_list_id = user32.SendMessageW(self.hwnd, TB_REPLACEBITMAP, 0, byref(rb))

        elif self.h_imagelist_dark:
            user32.SendMessageW(self.hwnd, TB_SETIMAGELIST, 0, self.h_imagelist_dark if is_dark else self.h_imagelist)

        if self.h_imagelist_disabled_dark:
            if is_dark:
                user32.SendMessageW(self.hwnd, TB_SETDISABLEDIMAGELIST, 0, self.h_imagelist_disabled_dark)
            else:
                user32.SendMessageW(self.hwnd, TB_SETDISABLEDIMAGELIST, 0, self.h_imagelist_disabled)

        if self.has_devider:
            if is_dark:
                self.register_message_callback(WM_NCPAINT, self._on_WM_NCPAINT)
            else:
                self.unregister_message_callback(WM_NCPAINT, self._on_WM_NCPAINT)

        # Update tooltip colors
        hwnd_tooltip = user32.SendMessageW(self.hwnd, TB_GETTOOLTIPS, 0, 0)
        if hwnd_tooltip:
            uxtheme.SetWindowTheme(hwnd_tooltip, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

        user32.SendMessageW(self.hwnd, TB_SETINSERTMARKCOLOR, 0, DARK_TEXT_COLOR if self.is_dark else 0)

    ########################################
    # Dark divider border at top
    ########################################
    def _on_WM_NCPAINT(self, hwnd, wparam, lparam):
        hdc = user32.GetWindowDC(hwnd)
        rc = self.get_window_rect()
        user32.FillRect(hdc, byref(RECT(0, 0, rc.right - rc.left, 1)), DARK_TOOLBAR_BORDER_BRUSH)
        user32.FillRect(hdc, byref(RECT(0, 1, rc.right - rc.left, 2)), DARK_BG_BRUSH)
        user32.ReleaseDC(hwnd, hdc)
        # An application returns zero if it processes this message
        return 0

    ########################################
    #
    ########################################
    def _on_WM_NOTIFY(self, hwnd, wparam, lparam):
        nmhdr = cast(lparam, POINTER(NMHDR)).contents
        msg = nmhdr.code
        if msg == NM_CUSTOMDRAW and nmhdr.hwndFrom == self.hwnd:

            nmtb = cast(lparam, POINTER(NMTBCUSTOMDRAW)).contents
            nmcd = nmtb.nmcd

            if nmcd.dwDrawStage == CDDS_PREPAINT:
                # Toolbar background
                user32.FillRect(nmcd.hdc, byref(nmcd.rc), self.bg_brush_dark if self.is_dark else self.bg_brush)

                if self.bottom_divider:
                    rc = self.get_client_rect()
                    if self.is_vertical:
                        rc.left = rc.right - 1
                    else:
                        rc.top = rc.bottom - 1
                    user32.FillRect(nmtb.nmcd.hdc, byref(rc), DARK_TOOLBAR_BORDER_BRUSH if self.is_dark else TOOLBAR_BORDER_BRUSH)
                return CDRF_NOTIFYITEMDRAW if self.is_dark else CDRF_DODEFAULT

            elif nmcd.dwDrawStage == CDDS_ITEMPREPAINT:

                # Only works with non-themed or style TBSTYLE_FLAT
                nmtb.clrText = DARK_TEXT_COLOR

#                nmtb.clrMark = 0x0000ff
#                nmtb.clrTextHighlight = 0x0000ff
#                gdi32.SetTextColor(nmcd.hdc, 0x00ff00)

#                nmtb.iListGap = 20

                if nmcd.uItemState & CDIS_HOT:
                    ########################################
                    # Hot (rollover) button state
                    ########################################
                    gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_ROLLOVER_BG_BRUSH)
                    gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_ROLLOVER_BORDER_PEN)
                    if nmcd.lItemlParam in self.dropdown_button_ids and not nmcd.lItemlParam in self.wholedropdown_button_ids:
                        gdi32.RoundRect(nmcd.hdc, nmcd.rc.left, nmcd.rc.top, nmcd.rc.right - 15, nmcd.rc.bottom - 1, 6, 6)
                    else:
                        gdi32.RoundRect(nmcd.hdc, nmcd.rc.left, nmcd.rc.top, nmcd.rc.right, nmcd.rc.bottom - 1, 6, 6)
                    return (TBCDRF_NOBACKGROUND | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES
                        | (CDRF_NOTIFYPOSTPAINT | TBCDRF_NOMARK if nmcd.lItemlParam in self.dropdown_button_ids else 0)
                    )

                elif nmcd.uItemState & CDIS_CHECKED:
                    ########################################
                    # Checked button state
                    ########################################
                    gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_CHECKED_BG_BRUSH)
                    gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_CHECKED_BORDER_PEN)
                    if nmcd.lItemlParam in self.dropdown_button_ids:
                        gdi32.RoundRect(nmcd.hdc, nmcd.rc.left, nmcd.rc.top, nmcd.rc.right - 15, nmcd.rc.bottom - 1, 6, 6)
                    else:
                        gdi32.RoundRect(nmcd.hdc, nmcd.rc.left, nmcd.rc.top, nmcd.rc.right, nmcd.rc.bottom - 1, 6, 6)
                    return (TBCDRF_NOBACKGROUND | TBCDRF_NOOFFSET | TBCDRF_NOETCHEDEFFECT | TBCDRF_NOEDGES
                        | (CDRF_NOTIFYPOSTPAINT | TBCDRF_NOMARK  if nmcd.lItemlParam in self.dropdown_button_ids else 0)
                    )

                else:
                    ########################################
                    # default button state
                    ########################################
                    if nmcd.lItemlParam in self.dropdown_button_ids:
                        return CDRF_NOTIFYPOSTPAINT

                return CDRF_DODEFAULT

            elif nmcd.dwDrawStage == CDDS_ITEMPOSTPAINT:

                def _draw_arrow(hdc, x, y):
                    hbr = gdi32.GetStockObject(WHITE_BRUSH)
                    user32.FillRect(hdc, byref(RECT(x,     y,      x + 7, y + 1)), hbr)
                    user32.FillRect(hdc, byref(RECT(x + 1, y + 1,  x + 6, y + 2)), hbr)
                    user32.FillRect(hdc, byref(RECT(x + 2, y + 2,  x + 5, y + 3)), hbr)
                    user32.FillRect(hdc, byref(RECT(x + 3, y + 3,  x + 4, y + 4)), hbr)

                if nmcd.lItemlParam in self.wholedropdown_button_ids:
                    _draw_arrow(nmcd.hdc, nmcd.rc.left + 21, nmcd.rc.top + 9)
                else:

                    if nmcd.uItemState & CDIS_HOT:
                        gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_ROLLOVER_BG_BRUSH)
                        gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_ROLLOVER_BORDER_PEN)
                        rc = RECT(nmcd.rc.right - 14, nmcd.rc.top - 4, nmcd.rc.right + 2, nmcd.rc.bottom + 4)
                        user32.FillRect(nmcd.hdc, byref(rc), DARK_BG_BRUSH)
                        gdi32.RoundRect(nmcd.hdc, rc.left, rc.top, rc.right, rc.bottom, 6, 6)

                    elif nmcd.uItemState & CDIS_CHECKED:
                        gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_CHECKED_BG_BRUSH)
                        gdi32.SelectObject(nmcd.hdc, DARK_TOOLBAR_BUTTON_CHECKED_BORDER_PEN)
                        rc = RECT(nmcd.rc.right - 14, nmcd.rc.top - 4, nmcd.rc.right + 2, nmcd.rc.bottom + 4)
                        user32.FillRect(nmcd.hdc, byref(rc), DARK_BG_BRUSH)
                        gdi32.RoundRect(nmcd.hdc, rc.left, rc.top, rc.right, rc.bottom , 6, 6)

                    _draw_arrow(nmcd.hdc, nmcd.rc.left + 23, nmcd.rc.top + 5)
                return CDRF_SKIPDEFAULT
