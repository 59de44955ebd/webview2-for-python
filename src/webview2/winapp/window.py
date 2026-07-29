from ctypes import *
from ctypes.wintypes import *

from .common_structs import *
from .const import *
from .dlls import *
from .types import *

hdc = user32.GetDC(None)
DPI_Y = gdi32.GetDeviceCaps(hdc, LOGPIXELSY)
user32.ReleaseDC(None, hdc)

H_FONT_SHELL = gdi32.CreateFontW(
    -11, 0, 0, 0, FW_DONTCARE, FALSE, FALSE, FALSE, ANSI_CHARSET, OUT_TT_PRECIS,
    CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, 'MS Shell Dlg'
)

HIGHLIGHT_COLOR = user32.GetSysColor(COLOR_HIGHLIGHT)
HIGHLIGHT_BRUSH = gdi32.CreateSolidBrush(HIGHLIGHT_COLOR)

# Macros
def MAKELONG(wLow, wHigh):
    return LONG(wLow | wHigh << 16).value

def MAKELPARAM(l, h):
    return LPARAM(MAKELONG(l, h)).value

def LOWORD(l):
    return WORD(l & 0xFFFF).value

def HIWORD(l):
    return WORD((l >> 16) & 0xFFFF).value

def MAKEINTRESOURCEA(x):
    return LPSTR(x)

def MAKEINTRESOURCEW(x):
    return LPCWSTR(x)

def GET_X_LPARAM(l):
    return SHORT(l & 0xFFFF).value

def GET_Y_LPARAM(l):
    return SHORT((l >> 16) & 0xFFFF).value

########################################
#
########################################
def center_window(hwnd, hwnd_parent = None):
    if hwnd_parent is None:
        hwnd_parent = user32.GetDesktopWindow()
    rc_parent = RECT()
    user32.GetWindowRect(hwnd_parent, byref(rc_parent))
    rc_window = RECT()
    user32.GetWindowRect(hwnd, byref(rc_window))
    width, height = rc_window.right - rc_window.left, rc_window.bottom - rc_window.top
    x = (rc_parent.left + rc_parent.right - width) // 2
    y = (rc_parent.top + rc_parent.bottom - height) // 2
    user32.SetWindowPos(hwnd, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)


########################################
#
########################################
class Window(object):

    ########################################
    #
    ########################################
    def __init__(
        self,
        window_class = None,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        left = 0, top = 0, width = 0, height = 0,
        window_title = None,
        wrap_hwnd = None,
        h_menu = None,
        h_font = H_FONT_SHELL
    ):
        self.children = []
        self.is_dark = False
        self.listeners = {}
        self.message_map = {}
        self.new_proc = None
        self.old_proc = None

        self.parent_window = parent_window
        if parent_window:
            parent_window.children.append(self)
#        self.is_dark = False
        self.visible = style & WS_VISIBLE

        self.has_border = (style & WS_BORDER) or (ex_style & WS_EX_CLIENTEDGE)

        if wrap_hwnd is not None:
            self.hwnd = wrap_hwnd
        else:
            self.hwnd = user32.CreateWindowExW(
                ex_style,
                window_class,
                window_title,
                style,
                left, top, width, height,
                parent_window.hwnd if parent_window else 0,
                h_menu,
                0,  # hInstance
                0   # lpParam
            )

        self.h_font = h_font
        user32.SendMessageW(self.hwnd, WM_SETFONT, self.h_font, MAKELPARAM(1, 0))

    ########################################
    #
    ########################################
    def destroy_window(self):
        if self.old_proc:
            user32.SetWindowLongPtrW(self.hwnd, GWL_WNDPROC, self.old_proc)
            self.message_map = {}
            self.old_proc = None
        user32.DestroyWindow(self.hwnd)

    ########################################
    #
    ########################################
    def window_proc_callback(self, hwnd, msg, wparam, lparam):
        if msg in self.message_map:
            for callback in self.message_map[msg]:
                res = callback(hwnd, wparam, lparam)
                if res is not None:
                    return res
        return self.old_proc(hwnd, msg, wparam, lparam)

    ########################################
    #
    ########################################
    def register_message_callback(self, msg, callback):
        if msg not in self.message_map:
            self.message_map[msg] = []
        self.message_map[msg].append(callback)
        if self.new_proc is None:
            self.new_proc = WNDPROC(self.window_proc_callback)
            self.old_proc = user32.SetWindowLongPtrW(self.hwnd, GWL_WNDPROC, self.new_proc)

    ########################################
    #
    ########################################
    def unregister_message_callback(self, msg, callback=None):
        if msg in self.message_map:
            if callback is None:
                del self.message_map[msg]
            elif callback in self.message_map[msg]:
                self.message_map[msg].remove(callback)
                if len(self.message_map[msg]) == 0:
                    del self.message_map[msg]

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):
        if is_dark == self.is_dark:
            return
        self.is_dark = is_dark
        for child in self.children:
            child.apply_theme(is_dark)

    def get_window_text(self, nMaxCount=255):
        buf = create_unicode_buffer(nMaxCount)
        user32.GetWindowTextW(self.hwnd, buf, nMaxCount)
        return buf.value

    def set_window_text(self, txt):
        user32.SetWindowTextW(self.hwnd, txt)

    def set_stayontop(self, flag=True):
        user32.SetWindowPos(self.hwnd, HWND_TOPMOST if flag else HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

    def set_layered(self):
        user32.SetWindowLongPtrA(self.hwnd, GWL_EXSTYLE,
                user32.GetWindowLongPtrA(self.hwnd, GWL_EXSTYLE) | WS_EX_LAYERED)

    def set_alpha(self, alpha):
        ''' only works if WS_EX_LAYERED was passed as ex_style to window_create'''
        user32.SetLayeredWindowAttributes(self.hwnd, 0, alpha, LWA_ALPHA)
        user32.RedrawWindow(self.hwnd, 0, 0, RDW_ERASE | RDW_INVALIDATE | RDW_FRAME | RDW_ALLCHILDREN)

    def resize_window(self, w, h):
        user32.SetWindowPos(self.hwnd, 0, 0, 0, w, h, SWP_NOMOVE)

    def activate_window(self):
        user32.SetActiveWindow(self.hwnd)

    def show(self, cmd_show=SW_SHOW):
        user32.ShowWindow(self.hwnd, cmd_show)
        self.visible = int(cmd_show > 0)

    def enable_window(self, flag):
        user32.EnableWindow(self.hwnd, flag)

    def set_window_pos(self, x=0, y=0, width=0, height=0, hwnd_insert_after=0, flags=0):
        user32.SetWindowPos(self.hwnd, hwnd_insert_after, x, y, width, height, flags)

    def set_foreground_window(self):
        user32.SetForegroundWindow(self.hwnd)

    def hide_focus_rects(self):
        user32.SendMessageW(self.hwnd, WM_CHANGEUISTATE, MAKELONG(UIS_SET, UISF_HIDEFOCUS), 0)

    def get_window_rect(self):
        rc = RECT()
        user32.GetWindowRect(self.hwnd, byref(rc))
        return rc

    def get_client_rect(self):
        rc = RECT()
        user32.GetClientRect(self.hwnd, byref(rc))
        return rc

    def send_message(self, msg, wparam=0, lparam=0):
        return user32.SendMessageW(self.hwnd, msg, wparam, lparam)

    def set_focus(self):
        user32.SetFocus(self.hwnd)

    def set_font(self, font_name=None, font_size=8, font_weight=FW_DONTCARE, font_italic=FALSE, h_font=None):
        if h_font is None:
            if font_name:
                cHeight = -kernel32.MulDiv(font_size, DPI_Y, 72)
                h_font = gdi32.CreateFontW(cHeight, 0, 0, 0, font_weight, font_italic, FALSE, FALSE, ANSI_CHARSET, OUT_TT_PRECIS,
                        CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, font_name)
            else:
                h_font = H_FONT_SHELL
        user32.SendMessageW(self.hwnd, WM_SETFONT, h_font, MAKELPARAM(1, 0))
        self.h_font = h_font

    def set_parent(self, win=None):
        user32.SetParent(self.hwnd, win.hwnd if win else None)

    def get_children(self):
        children = []
        def _enum_child_func(hwnd, lparam):
            children.append(hwnd)
            return TRUE
        user32.EnumChildWindows(self.hwnd, WNDENUMPROC(_enum_child_func), 0)
        return children

    def move_window(self, x, y, width, height, repaint=1):
        return user32.MoveWindow(self.hwnd, x, y, width, height, repaint)

    def update_window(self):
        user32.UpdateWindow(self.hwnd)

    def redraw_window(self):
        user32.RedrawWindow(self.hwnd, 0, 0, RDW_ERASE | RDW_INVALIDATE | RDW_FRAME | RDW_ALLCHILDREN)

    def force_redraw_window(self):
        user32.SetWindowPos(self.hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)

    def get_dropped_items(self, hdrop):
        dropped_items = []
        cnt = shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
        for i in range(cnt):
            file_buffer = create_unicode_buffer('', MAX_PATH)
            shell32.DragQueryFileW(hdrop, i, file_buffer, MAX_PATH)
            dropped_items.append(file_buffer[:].split('\0', 1)[0])
        shell32.DragFinish(hdrop)
        return dropped_items

#    def center_window(self, hwnd_parent = None):
#        if hwnd_parent is None:
#            hwnd_parent = user32.GetDesktopWindow()
#        rc_parent = RECT()
#        user32.GetClientRect(hwnd_parent, byref(rc_parent))
#        rc_window = RECT()
#        user32.GetWindowRect(self.hwnd, byref(rc_window))
#        width, height = rc_window.right - rc_window.left, rc_window.bottom - rc_window.top
#        x = (rc_parent.right - width) // 2
#        y = (rc_parent.bottom - height) // 2
#        user32.SetWindowPos(self.hwnd, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)

    def connect(self, evt, func):
        if evt not in self.listeners:
            self.listeners[evt] = []
        self.listeners[evt].append(func)

    def disconnect(self, evt, func):
        if evt not in self.listeners:
            return
        if func in self.listeners[evt]:
            self.listeners[evt].remove(func)

    def emit(self, evt, *args):
        if evt not in self.listeners:
            return
        for func in self.listeners[evt]:
            func(*args)
