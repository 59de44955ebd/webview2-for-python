from ..controls.tabcontrol import *
from ..themes import *

DARK_TAB_BG_BRUSH = DARK_BG_BRUSH
DARK_TAB_ROLLOVER_BG_BRUSH = gdi32.CreateSolidBrush(0x363636)
DARK_TAB_SELECTED_BG_BRUSH = gdi32.CreateSolidBrush(0x3B3B3B)
DARK_TAB_BORDER_BRUSH = gdi32.CreateSolidBrush(0x484848)

#DARK_TAB_BG_BRUSH = gdi32.CreateSolidBrush(0x383838)
#DARK_TAB_SELECTED_BG_BRUSH = gdi32.CreateSolidBrush(0x121212)

TAB_BG_BRUSH = gdi32.CreateSolidBrush(0xF3F3F3)
TAB_SELECTED_BG_BRUSH = gdi32.CreateSolidBrush(0xFFFFFF)  # 0xF9F9F9
TAB_ROLLOVER_BG_BRUSH = gdi32.CreateSolidBrush(0xEDEDED)
TAB_BORDER_BRUSH = gdi32.CreateSolidBrush(0xF0F0F0)

TIMER_ID_MOVE = 1000

EVENT_TAB_MOVED = 1
EVENT_TAB_CLOSE_REQUESTED = 2


########################################
# Wrapper Class
########################################
class TabControl(TabControl):

    ########################################
    #
    ########################################
    def __init__(
        self,
        *args,
        close_button_imagelist = None,
        tabs_movable = True,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._close_button_imagelist = close_button_imagelist

        self._hover_index = -1
        self._close_button_hover_index = -1

        self.hwnd_updown = None

        self.register_message_callback(WM_PAINT, self._on_WM_PAINT)
        self.register_message_callback(WM_SIZE, self._on_WM_SIZE)

        ########################################
        # Prevents visual artifacts around the UpDown control
        ########################################
        def _on_WM_HSCROLL(hwnd, wparam, lparam):
            user32.RedrawWindow(self.hwnd, 0, 0, RDW_INVALIDATE)

        self.register_message_callback(WM_HSCROLL, _on_WM_HSCROLL)

        if tabs_movable:
            self._moved_tab_index = None
            self._hcr_move = user32.LoadCursorW(None, IDC_SIZEWE)

            ########################################
            #
            ########################################
            def _on_WM_TIMER(hwnd, wparam, lparam):
                user32.KillTimer(self.hwnd, wparam)
                user32.SetCursor(self._hcr_move)

            ########################################
            #
            ########################################
            def _on_WM_LBUTTONDOWN(hwnd, wparam, lparam):
                x, y = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                pt = POINT(x, y)
                idx = user32.SendMessageW(self.hwnd, TCM_HITTEST, 0, byref(TCHITTESTINFO(pt, 0)))
                if idx < 0:
                    return

                if idx == self.get_cur_sel():
                    rc = self.get_item_rect(idx)
                    if x >= rc.right - 18:
                        self.emit(EVENT_TAB_CLOSE_REQUESTED, idx)
                        return

                self._moved_tab_index = idx

                # If mouse is pressed for more than 400 ms, we assume the user
                # wants to move the tab and show a corresponding cursor
                self.register_message_callback(WM_TIMER, _on_WM_TIMER)
                user32.SetTimer(self.hwnd, TIMER_ID_MOVE, 400, 0)

                user32.SetCapture(hwnd)

            self.register_message_callback(WM_LBUTTONDOWN, _on_WM_LBUTTONDOWN)

            ########################################
            #
            ########################################
            def _on_WM_LBUTTONUP(hwnd, wparam, lparam):
                if self._moved_tab_index is not None:
                    user32.KillTimer(self.hwnd, TIMER_ID_MOVE)
                    self.unregister_message_callback(WM_TIMER, _on_WM_TIMER)
                    user32.SetCursor(None)
                    user32.ReleaseCapture()

                    x, y = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                    pt = POINT(x, y)
                    idx = user32.SendMessageW(self.hwnd, TCM_HITTEST, 0, byref(TCHITTESTINFO(pt, 0)))

                    if idx < 0:
                        rc = self.get_client_rect()
                        x, y = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                        if user32.PtInRect(byref(rc), POINT(x, y)):
                            idx = self.get_item_count() - 1

                    if idx >= 0 and idx != self._moved_tab_index:
                        tie = TCITEMW()
                        tie.mask = TCIF_TEXT | TCIF_PARAM | TCIF_IMAGE
                        tie.pszText = cast(create_unicode_buffer(MAX_TAB_TEXT_LEN + 1), LPWSTR)
                        tie.cchTextMax = MAX_TAB_TEXT_LEN
                        user32.SendMessageW(self.hwnd, TCM_GETITEMW, self._moved_tab_index, byref(tie))
                        user32.SendMessageW(self.hwnd, TCM_DELETEITEM, self._moved_tab_index, 0)
                        self.insert_item(idx, tie)
                        self.emit(EVENT_TAB_MOVED, self._moved_tab_index, idx)  # old_index, new_index
                    self._moved_tab_index = None

            self.register_message_callback(WM_LBUTTONUP, _on_WM_LBUTTONUP)

        ########################################
        #
        ########################################
        def _on_WM_MOUSEMOVE(hwnd, wparam, lparam):
            x, y = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            pt = POINT(x, y)
            idx = user32.SendMessageW(self.hwnd, TCM_HITTEST, 0, byref(TCHITTESTINFO(pt, 0)))

            if idx != self._hover_index:
                rc = RECT()
                if self._hover_index >= 0:
                    user32.SendMessageW(self.hwnd, TCM_GETITEMRECT, self._hover_index, byref(rc))
                    user32.InvalidateRect(self.hwnd, byref(rc), TRUE)
                self._hover_index = idx
                if self._hover_index >= 0:
                    user32.SendMessageW(self.hwnd, TCM_GETITEMRECT, self._hover_index, byref(rc))
                    user32.InvalidateRect(self.hwnd, byref(rc), TRUE)

            if idx < 0:
                return

            rc = self.get_item_rect(idx)
            if x >= rc.right - 18:
                if idx != self._close_button_hover_index:
                    self._close_button_hover_index = idx
                    user32.InvalidateRect(self.hwnd, byref(rc), TRUE)
            elif self._close_button_hover_index >= 0:
                rc = self.get_item_rect(self._close_button_hover_index)
                self._close_button_hover_index = -1
                user32.InvalidateRect(self.hwnd, byref(rc), TRUE)

        self.register_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)

        ########################################
        #
        ########################################
        def _on_WM_MOUSELEAVE(hwnd, wparam, lparam):
            if self._hover_index >= 0:
                rc = RECT()
                user32.SendMessageW(self.hwnd, TCM_GETITEMRECT, self._hover_index, byref(rc))
                self._hover_index = -1
                user32.InvalidateRect(self.hwnd, byref(rc), TRUE)

            if self._close_button_hover_index >= 0:
                rc = self.get_item_rect(self._close_button_hover_index)
                self._close_button_hover_index = -1
                user32.InvalidateRect(self.hwnd, byref(rc), TRUE)

        self.register_message_callback(WM_MOUSELEAVE, _on_WM_MOUSELEAVE)

    ########################################
    #
    ########################################
    def _on_WM_PAINT(self, hwnd, wparam, lparam):
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(hwnd, byref(ps))
        gdi32.SetBkMode(hdc, TRANSPARENT)
        gdi32.SetTextColor(hdc, DARK_TEXT_COLOR if self.is_dark else 0x000000)
        gdi32.SelectObject(hdc, self.h_font)

        # Tabbar background
        user32.FillRect(hdc, byref(ps.rcPaint), DARK_BG_BRUSH if self.is_dark else self._bg_brush)

        himl = user32.SendMessageW(self.hwnd, TCM_GETIMAGELIST, 0, 0)

        pt = POINT()
        user32.GetCursorPos(byref(pt))
        user32.MapWindowPoints(None, self.hwnd, byref(pt), 1)

#        rollover_idx = user32.SendMessageW(self.hwnd, TCM_HITTEST, 0, byref(TCHITTESTINFO(pt, 0)))
        rollover_idx = self._hover_index

        buf = create_unicode_buffer(MAX_TAB_TEXT_LEN)
        tc_item = TCITEMW()
        tc_item.mask = TCIF_TEXT | TCIF_IMAGE
        tc_item.cchTextMax = MAX_TAB_TEXT_LEN

        rc = RECT()

        selected_index = self.get_cur_sel()
        for idx in range(self.get_item_count()):

            user32.SendMessageW(self.hwnd, TCM_GETITEMRECT, idx, byref(rc))

            rc.left -= 1
            if idx != selected_index:
                rc.top += 2

            # Tab border
            user32.FillRect(hdc, byref(rc), DARK_TAB_BORDER_BRUSH if self.is_dark else TAB_BORDER_BRUSH)

            # Tab background
            rc.left += 1
            rc.right -= 1
            rc.top += 1

            if idx == selected_index:
                user32.FillRect(hdc, byref(rc), DARK_TAB_SELECTED_BG_BRUSH if self.is_dark else TAB_SELECTED_BG_BRUSH)

            elif idx == rollover_idx:
                user32.FillRect(hdc, byref(rc), DARK_TAB_ROLLOVER_BG_BRUSH if self.is_dark else TAB_ROLLOVER_BG_BRUSH)

            else:
                user32.FillRect(hdc, byref(rc), DARK_TAB_BG_BRUSH if self.is_dark else TAB_BG_BRUSH)

            tc_item.pszText = cast(buf, LPWSTR)
            user32.SendMessageW(self.hwnd, TCM_GETITEMW, idx, byref(tc_item))

            if tc_item.iImage >= 0:
                comctl32.ImageList_Draw(himl, tc_item.iImage, hdc, rc.left + 6, rc.top + 3, ILD_NORMAL)
#               user32.DrawIconEx(hdc_dest, x, 0, h_icon, ico_size, ico_size, 0, None, DI_NORMAL)

            if idx == selected_index:
                user32.DrawTextW(hdc, buf.value, -1, RECT(rc.left + 30, rc.top, rc.right - 18, rc.bottom), DT_SINGLELINE | DT_VCENTER | DT_END_ELLIPSIS)

                if idx == self._close_button_hover_index:
#                    user32.FillRect(hdc, byref(RECT(rc.right - 17, rc.top + 5, rc.right - 3, rc.top + 19)), DARK_TAB_BG_BRUSH if self.is_dark else TAB_BORDER_BRUSH)

                    gdi32.SelectObject(hdc, gdi32.GetStockObject(NULL_PEN))
                    gdi32.SelectObject(hdc, gdi32.GetStockObject(BLACK_BRUSH) if self.is_dark else TAB_BORDER_BRUSH)
                    gdi32.RoundRect(hdc, rc.right - 17, rc.top + 5, rc.right - 2, rc.top + 20, 5, 5)

                comctl32.ImageList_Draw(
                    self._close_button_imagelist,
                    1 if self.is_dark else 0,
                    hdc,
                    rc.right - 18, rc.top + 4,
                    ILD_NORMAL
                )
#                if idx == self._close_button_hover_index:
#                    user32.InvertRect(hdc, byref(RECT(rc.right - 15, rc.top + 6, rc.right - 3, rc.top + 18)))

            else:
                user32.DrawTextW(hdc, buf.value, -1, RECT(rc.left + 30, rc.top, rc.right - 8, rc.bottom), DT_SINGLELINE | DT_VCENTER | DT_END_ELLIPSIS)

        user32.EndPaint(hwnd, byref(ps))

        if self.hwnd_updown is None:
            self.hwnd_updown = user32.FindWindowExW(self.hwnd, NULL, 'msctls_updown32', '')
            if self.hwnd_updown:
                uxtheme.SetWindowTheme(self.hwnd_updown, 'DarkMode_Explorer' if self.is_dark else 'Explorer', None)

        return FALSE

    ########################################
    #
    ########################################
    def _on_WM_SIZE(self, hwnd, wparam, lparam):
        if self.hwnd_updown is None:
            self.hwnd_updown = user32.FindWindowExW(self.hwnd, NULL, 'msctls_updown32', '')
            if self.hwnd_updown:
                uxtheme.SetWindowTheme(self.hwnd_updown, 'DarkMode_Explorer' if self.is_dark else 'Explorer', None)

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        if is_dark == self.is_dark:
            return
        super().apply_theme(is_dark)

        if self.hwnd_updown:
            uxtheme.SetWindowTheme(self.hwnd_updown, 'DarkMode_Explorer' if is_dark else 'Explorer', None)

        hwnd_tooltips = user32.SendMessageW(self.hwnd, TCM_GETTOOLTIPS, 0, 0)
        if hwnd_tooltips:
            uxtheme.SetWindowTheme(hwnd_tooltips, 'DarkMode_Explorer' if is_dark else 'Explorer', None)
