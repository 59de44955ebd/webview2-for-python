from ..window import *
from ..themes import *

SPLITTER_SIZE = 4

EVENT_SPLITTER_MOVING_STARTED = 2
EVENT_SPLITTER_MOVED = 0
EVENT_SPLITTER_MOVING = 1

#SPLITTER_BRUSH_LIGHT = gdi32.CreateSolidBrush(0xF3F3F3)  # COLOR_3DFACE + 1
#SPLITTER_BRUSH_DARK = DARK_BG_BRUSH

SPLITTER_BRUSH_MOVING = gdi32.CreateSolidBrush(0x808080)

def _window_proc_callback(hwnd, msg, wparam, lparam):
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

_window_proc = WNDPROC(_window_proc_callback)


########################################
#
########################################
class Splitter(Window):

    def __init__(
        self,
        parent_window,
        style = WS_CHILD,
        height = 0,
        pos_min = 0, pos_max = 0xffff, initial_pos = 0,
        is_vertical = False,
        is_reversed = False,
        bg_brush = COLOR_3DFACE + 1,
        bg_brush_dark = DARK_BG_BRUSH
    ):
        self.pos = initial_pos
        self.pos_min = pos_min
        self.pos_max = pos_max
        self.is_vertical = is_vertical
        self.is_reversed = is_reversed
        self.bg_brush = bg_brush
        self.bg_brush_dark = bg_brush_dark

        self.x = 0
        self.y = 0

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = _window_proc
        newclass.style = CS_VREDRAW | CS_HREDRAW
        newclass.lpszClassName = 'SplitterClass'
        newclass.hbrBackground = bg_brush
        newclass.hCursor = user32.LoadCursorW(0, IDC_SIZENS if is_vertical else IDC_SIZEWE)
        user32.RegisterClassExW(byref(newclass))

        super().__init__(
            newclass.lpszClassName,
            style = style,
            parent_window = parent_window,
            left = 0 if is_vertical else initial_pos,
            top = initial_pos if is_vertical else 0,
            width = 0 if is_vertical else SPLITTER_SIZE,
            height = SPLITTER_SIZE if is_vertical else 0,
#            left = initial_pos,
#            width = SPLITTER_SIZE,
#            height = height
        )

        ########################################
        #
        ########################################
        def _on_WM_MOUSEMOVE(hwnd, wparam, lparam):
            if self.is_vertical:
                y = GET_Y_LPARAM(lparam) - self._click_y
                pt = POINT(0, y)
                user32.MapWindowPoints(self.hwnd, self.parent_window.hwnd, byref(pt), 1)
                if self.is_reversed:
                    self.y = max(min(pt.y, self.rc_parent.bottom - self.pos_min - SPLITTER_SIZE), self.rc_parent.bottom - self.__pos_max)
                    self.pos = self.rc_parent.bottom - self.y - SPLITTER_SIZE
                else:
                    self.y = self.pos = max(min(pt.y, self.__pos_max), self.pos_min)
            else:
                x = GET_X_LPARAM(lparam) - self._click_x
                pt = POINT(x, 0)
                user32.MapWindowPoints(self.hwnd, self.parent_window.hwnd, byref(pt), 1)
                if self.is_reversed:
                    self.x = max(min(pt.x, self.rc_parent.right - self.pos_min - SPLITTER_SIZE), self.rc_parent.right - self.__pos_max)
                    self.pos = self.rc_parent.right - self.x - SPLITTER_SIZE
                else:
                    self.x = self.pos = max(min(pt.x, self.__pos_max), self.pos_min)

            user32.SetWindowPos(self.hwnd, 0, self.x, self.y, 0, 0, SWP_NOSIZE)  # | SWP_NOZORDER | SWP_NOACTIVATE)
            self.emit(EVENT_SPLITTER_MOVING)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONDOWN(hwnd, wparam, lparam):
            if self.is_vertical:
                self._click_y = GET_Y_LPARAM(lparam)
                if self.is_reversed:
                    self.rc_parent = self.parent_window.get_client_rect()
                self.register_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)
                user32.SetCapture(hwnd)
                user32.SetClassLongPtrW(self.hwnd, GCLP_HBRBACKGROUND, SPLITTER_BRUSH_MOVING)
                self.redraw_window()
                if type(self.pos_max) == Splitter:
                    self.__pos_max = self.rc_parent.bottom - self.pos_max.y - SPLITTER_SIZE if self.is_reversed else self.pos_max.y - SPLITTER_SIZE
                else:
                    self.__pos_max = self.pos_max
            else:
                self._click_x = GET_X_LPARAM(lparam)
                if self.is_reversed:
                    self.rc_parent = self.parent_window.get_client_rect()
                self.register_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)
                user32.SetCapture(hwnd)
                user32.SetClassLongPtrW(self.hwnd, GCLP_HBRBACKGROUND, SPLITTER_BRUSH_MOVING)
                self.redraw_window()
                if type(self.pos_max) == Splitter:
                    self.__pos_max = self.rc_parent.right - self.pos_max.x - SPLITTER_SIZE if self.is_reversed else self.pos_max.x - SPLITTER_SIZE
                else:
                    self.__pos_max = self.pos_max

            user32.SetWindowPos(self.hwnd, HWND_TOP, 0, 0, 0, 0, SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE)
            user32.SetFocus(self.hwnd)

            self.emit(EVENT_SPLITTER_MOVING_STARTED)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONUP(hwnd, wparam, lparam):
            user32.ReleaseCapture()
            self.unregister_message_callback(WM_MOUSEMOVE, _on_WM_MOUSEMOVE)
            user32.SetClassLongPtrW(self.hwnd, GCLP_HBRBACKGROUND, self.bg_brush_dark if self.is_dark else self.bg_brush)
            self.redraw_window()

            self.emit(EVENT_SPLITTER_MOVED)  #, self.x)

        self.register_message_callback(WM_LBUTTONDOWN, _on_WM_LBUTTONDOWN)
        self.register_message_callback(WM_LBUTTONUP, _on_WM_LBUTTONUP)

    ########################################
    # relative to parent
    ########################################
    def apply_theme(self, is_dark):
        self.is_dark = is_dark
        user32.SetClassLongPtrW(self.hwnd, GCLP_HBRBACKGROUND, self.bg_brush_dark if self.is_dark else self.bg_brush)

    ########################################
    # relative to parent
    ########################################
    def set_min(self, pos_min):
        self.pos_min = pos_min

    ########################################
    # relative to parent, from the right/bottom
    ########################################
    def set_max(self, pos_max):
        self.pos_max = pos_max

    ########################################
    #
    ########################################
    def set_window_pos(self, x=0, y=0, width=0, height=0, hwnd_insert_after=0, flags=0):
        self.x, self.y = x, y
        user32.SetWindowPos(self.hwnd, hwnd_insert_after, x, y, width, height, flags)
