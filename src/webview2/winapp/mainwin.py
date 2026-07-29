from .window import *


########################################
# Wrapper Class
########################################
class MainWin(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        window_title = 'MyPythonApp',
        window_class = 'MyPythonAppClass',
        left = None, top = None, width = 1024, height = 768,
        style = WS_OVERLAPPEDWINDOW,
        ex_style = 0,
        class_style = CS_VREDRAW | CS_HREDRAW,

        h_accel = None,
        h_brush = COLOR_WINDOW + 1,
        h_cursor = None,
        h_icon = None,
        h_menu = None,
    ):
        self.h_accel = h_accel
        self.h_brush = h_brush
        self.h_icon = h_icon
        self.h_menu = h_menu

        self.window_title = window_title
        self.timers = {}
        self.timer_id_counter = 1000

        ########################################
        #
        ########################################
        def _on_WM_TIMER(hwnd, wparam, lparam):
            if wparam in self.timers:
                callback = self.timers[wparam][0]
                if self.timers[wparam][1]:
                    user32.KillTimer(self.hwnd, wparam)
                    del self.timers[wparam]
                callback()
            return 0

        self._message_map = {
            WM_TIMER:        [_on_WM_TIMER],
            WM_CLOSE:        [self.quit],
        }

        ########################################
        #
        ########################################
        def _window_proc_callback(hwnd, msg, wparam, lparam):
            if msg in self._message_map:
                for callback in self._message_map[msg]:
                    res = callback(hwnd, wparam, lparam)
                    if res is not None:
                        return res
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        self.windowproc = WNDPROC(_window_proc_callback)

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = self.windowproc
        newclass.style = class_style
        newclass.lpszClassName = window_class
        newclass.hbrBackground = h_brush
        newclass.hCursor = h_cursor if h_cursor is not None else user32.LoadCursorW(None, IDC_ARROW)
        newclass.hIcon = self.h_icon
        user32.RegisterClassExW(byref(newclass))

        if left is None or top is None:
            rc = RECT()
            user32.GetClientRect(user32.GetDesktopWindow(), byref(rc))
            left, top = (rc.right - width) // 2, (rc.bottom - height) // 2

        super().__init__(
            newclass.lpszClassName,
            style = style,
            ex_style = ex_style,
            left = left, top = top, width = width, height = height,
            window_title = window_title,
            h_menu = h_menu,
        )

    ########################################
    #
    ########################################
    def create_timer(self, callback, ms, is_singleshot=False, timer_id=None):
        if timer_id is None:
            timer_id = self.timer_id_counter
            self.timer_id_counter += 1
        self.timers[timer_id] = (callback, is_singleshot)
        user32.SetTimer(self.hwnd, timer_id, ms, 0)
        return timer_id

    ########################################
    #
    ########################################
    def kill_timer(self, timer_id):
        if timer_id in self.timers:
            user32.KillTimer(self.hwnd, timer_id)
            del self.timers[timer_id]

    ########################################
    #
    ########################################
    def register_message_callback(self, msg, callback, overwrite=False):
        if overwrite:
            self._message_map[msg] = [callback]
        else:
            if msg not in self._message_map:
                self._message_map[msg] = []
            self._message_map[msg].append(callback)

    ########################################
    #
    ########################################
    def unregister_message_callback(self, msg, callback=None):
        if msg in self._message_map:
            if callback is None:  # was: == True
                del self._message_map[msg]
            elif callback in self._message_map[msg]:
                self._message_map[msg].remove(callback)
                if len(self._message_map[msg]) == 0:
                    del self._message_map[msg]

    ########################################
    #
    ########################################
    def run(self):
        msg = MSG()
        while user32.GetMessageW(byref(msg), None, 0, 0):
            if self.h_accel and user32.TranslateAcceleratorW(self.hwnd, self.h_accel, byref(msg)):
                continue
            elif user32.IsDialogMessage(self.hwnd, byref(msg)):
                continue
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))
        return 0

    ########################################
    #
    ########################################
    def quit(self, *args):
        user32.PostQuitMessage(0)
