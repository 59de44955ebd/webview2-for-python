from .. import *
from ..winapp.const import *
from ..winapp.themes import *
from ..winapp.window import *


########################################
#
########################################
class WebView2(WebView2):

    ########################################
    #
    ########################################
    def __init__(self, parent_window, *args, **kwargs):

        self._controller = None

        ########################################
        #
        ########################################
        def _window_proc_callback(hwnd, msg, wparam, lparam):
            if msg == WM_SIZE:
                width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                self.put_bounds(RECT(0, 0, width, height))
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        self.windowproc = WNDPROC(_window_proc_callback)

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = self.windowproc
        newclass.style = 0
        newclass.lpszClassName = 'WebView2Window'
        newclass.hbrBackground = COLOR_WINDOW + 1
        newclass.hCursor = user32.LoadCursorW(None, IDC_ARROW)
        user32.RegisterClassExW(byref(newclass))

        self.window = Window(
            newclass.lpszClassName,
            parent_window = parent_window,
#            window_title = window_title,
        )

        super().__init__(parent_hwnd = self.window.hwnd, *args, **kwargs)
