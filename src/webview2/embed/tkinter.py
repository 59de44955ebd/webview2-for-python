from .. import *

from ..winapp.const import *
from ..winapp.dlls import user32
from ..winapp.types import WNDPROC
from ..winapp.window import *
from ..winapp.themes import *

import tkinter as tk

SETTINGS.ALLOW_HOST_INPUT_PROCESSING = True

########################################
#
########################################
def center_window(window, width, height):
    """Centers the window to the main display/monitor"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

########################################
#
########################################
def set_menu_background(hmenu: int, brush: int):
    menu_info = MENUINFO()
    menu_info.cbSize = sizeof(MENUINFO)
    menu_info.fMask = MIM_BACKGROUND | MIM_APPLYTOSUBMENUS
    menu_info.hbrBack = brush
    user32.SetMenuInfo(hmenu, byref(menu_info))


########################################
#
########################################
class StatusBar(tk.Frame):

    def __init__(self, master, text = ''):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, text = text)
        self.label.pack(side = tk.LEFT)
        self.pack(fill=tk.X, side = tk.BOTTOM)

    def set_text(self, text):
        self.label.config(text = text)

    def apply_theme(self, is_dark):
        if is_dark:
            self.configure(background='#202020')
            self.label.configure(bg='#202020', fg='white')
        else:
            self.configure(background='SystemButtonFace')
            self.label.configure(bg='SystemButtonFace', fg='black')


########################################
#
########################################
class WebView2(WebView2):

    ########################################
    #
    ########################################
    def __init__(self, root, menubar = None, statusbar = False, *args, **kwargs):

        self._webview_frame = tk.Frame(root)

        super().__init__(
            parent_hwnd = self._webview_frame.winfo_id(),
            *args,
            **kwargs
        )

        self._webview_frame.bind('<Configure>', self.on_resize)
        self._webview_frame.pack(expand = True, fill = tk.BOTH)

        self._root = root

        self._menubar = menubar
        if menubar:
            root.config(menu=menubar)
            self._blank_menubar = tk.Menu(root)

        if statusbar:
            self._statusbar = StatusBar(root)
        else:
            self._statusbar = None

        self._fullscreen = False
        self._is_dark = False

        self._hwnd_main = user32.GetParent(self._root.winfo_id())

        if self._menubar:
#            hwnd_tk = root.winfo_id()
#            hwnd_tk = self._hwnd_main
            self._wrapper = Window(wrap_hwnd = self._hwnd_main)

            ########################################
            #
            ########################################
            def _on_webview_ready(webview):

                # Subclass WebView2 to forward key events to tkinter
                def window_proc_callback(hwnd, msg, wparam, lparam):
                    if msg in (WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP) and user32.GetFocus() == self.hwnd:
                        user32.SetFocus(self._hwnd_main)
                        user32.SendMessageW(self._hwnd_main, msg, wparam, lparam)
                        user32.SetFocus(self.hwnd)
                    return self.old_proc(hwnd, msg, wparam, lparam)

                self.new_proc = WNDPROC(window_proc_callback)
                self.old_proc = user32.SetWindowLongPtrW(self.hwnd, GWL_WNDPROC, self.new_proc)

            self.connect(EVENT.WEBVIEW_READY, _on_webview_ready)

    ########################################
    #
    ########################################
    def on_resize(self, event):
        self.put_bounds(RECT(0, 0, event.width, event.height))

    ########################################
    #
    ########################################
    def close(self):
        self._root.destroy()

    ########################################
    # We do NOT use attributes("-fullscreen") because this would create a new window with a new HWND
    # whenever called, so we would have to subclass the window again (for having a dark menubar in dark mode).
    ########################################
    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            if self._menubar:
                self._root.config(menu=self._blank_menubar)
            if self._statusbar:
                self._statusbar.pack_forget()
        else:
            if self._menubar:
                self._root.config(menu=self._menubar)
            if self._statusbar:
                self._statusbar.pack(fill=tk.X, side = tk.BOTTOM)

        style = user32.GetWindowLongA(self._hwnd_main, GWL_STYLE)
        if self._fullscreen:
            style &= ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
        else:
            style |= (WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
        user32.SetWindowLongA(self._hwnd_main, GWL_STYLE, style)
        user32.ShowWindow(self._hwnd_main, SW_SHOWMAXIMIZED if self._fullscreen else SW_NORMAL)

        if self._menubar and not self._fullscreen and self._is_dark:
            self._root.update()
            set_menu_background(user32.GetMenu(self._hwnd_main), DARK_BG_BRUSH)

    ########################################
    #
    ########################################
    def escape_fullscreen(self):
        if self._fullscreen:
            self.toggle_fullscreen()

    ########################################
    #
    ########################################
    def apply_theme(self, preferred_color_scheme = PREFERRED_COLOR_SCHEME.AUTO):

        if self.webview_ready:
            self.profile_apply_theme(preferred_color_scheme)

        is_dark = reg_should_use_dark_mode() if preferred_color_scheme == PREFERRED_COLOR_SCHEME.AUTO else preferred_color_scheme == PREFERRED_COLOR_SCHEME.DARK

        hwnd_main = user32.GetParent(self._root.winfo_id())

        # Update colors of window titlebar
        dwm_use_dark_mode(hwnd_main, is_dark)

        if self._statusbar:
            self._statusbar.apply_theme(is_dark)

        if self._menubar:
            bg = '#202020' if is_dark else 'SystemMenu'
            fg = 'white' if is_dark else 'black'
            def update_menu(parent_menu):
                for menu in parent_menu.children.values():
                    menu.configure(bg = bg, fg = fg)
                    update_menu(menu)

            update_menu(self._menubar)

            # Subclass tkinter (or restore original window proc)
            theme_menubar(self._wrapper, is_dark)

            set_menu_background(user32.GetMenu(hwnd_main), DARK_BG_BRUSH if is_dark else None)

            user32.RedrawWindow(hwnd_main, 0, 0, RDW_FRAME | RDW_ERASE | RDW_INVALIDATE)

#       self._root.configure(bg='#202020' if is_dark else 'white')

        self._is_dark = is_dark

    ########################################
    #
    ########################################
    def set_status_bar_text(self, text):
        if self._statusbar:
            self._statusbar.set_text(text)
