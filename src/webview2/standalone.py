from webview2 import *

from webview2.winapp.controls_themed.statusbar import *
from webview2.winapp.dialogs import *
from webview2.winapp.mainwin_themed import *

SETTINGS.ALLOW_HOST_INPUT_PROCESSING = True


########################################
#
########################################
class WebView2(WebView2):

    ########################################
    #
    ########################################
    def __init__(
        self,
        window_title = 'WebView',
        h_accel = None,
        h_icon = None,
        h_menu = None,
        statusbar = False,
        left = None, top = None, width = 1024, height = 768,
        color_scheme = PREFERRED_COLOR_SCHEME.AUTO,
        *args,
        **kwargs,
    ):
        self._fullscreen = False
        self._statusbar = None

        if left is None or top is None:
            # Show centered on desktop
            rc = RECT()
            user32.GetClientRect(user32.GetDesktopWindow(), byref(rc))
            left, top = (rc.right - width) // 2, (rc.bottom - height) // 2

        self._mainwin = MainWin(
            window_title = window_title,
            window_class = 'WebView2Standalone',
            style = WS_OVERLAPPEDWINDOW | WS_VISIBLE,
            left = left, top = top, width = width, height = height,
            h_accel = h_accel,
            h_icon = h_icon,
            h_menu = h_menu,
        )

        rc = RECT()
        user32.GetClientRect(self._mainwin.hwnd, byref(rc))
        width, height = rc.right, rc.bottom

        if statusbar:
            self._statusbar = StatusBar(self._mainwin)
            height -= self._statusbar.height

        super().__init__(
            parent_hwnd = self._mainwin.hwnd,
            width = width, height = height,
            *args,
            **kwargs
        )

        self.set_theme(color_scheme)

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            if self._statusbar:
                self._statusbar.update_size()
                if user32.IsWindowVisible(self._statusbar.hwnd):
                    height -= self._statusbar.height
            self.put_bounds(RECT(0, 0, width, height))

        self._mainwin.register_message_callback(WM_SIZE, _on_WM_SIZE)

        ########################################
        #
        ########################################
        def _on_WM_COMMAND(hwnd, wparam, lparam):
            self.emit(EVENT.MENU_COMMAND, LOWORD(wparam))

        self._mainwin.register_message_callback(WM_COMMAND, _on_WM_COMMAND)

        if h_menu and hasattr(self, 'on_menu'):
            self.connect(EVENT.MENU_COMMAND, self.on_menu)

        if hasattr(self, 'on_webview_ready'):
            self.connect(EVENT.WEBVIEW_READY, self.on_webview_ready)

        if hasattr(self, 'on_dom_content_loaded'):
            self.connect(EVENT.DOM_CONTENT_LOADED, self.on_dom_content_loaded)

        if hasattr(self, 'on_status_bar_text_changed'):
            self.connect(EVENT.STATUS_BAR_TEXT_CHANGED, self.on_status_bar_text_changed)

        ########################################
        #
        ########################################
        def _on_WM_SETTINGCHANGE(hwnd, wparam, lparam):
            if self._color_scheme != PREFERRED_COLOR_SCHEME.AUTO:
                return
            if lparam and cast(lparam, LPCWSTR).value == 'ImmersiveColorSet':
                self._mainwin.apply_theme(reg_should_use_dark_mode())

        self._mainwin.register_message_callback(WM_SETTINGCHANGE, _on_WM_SETTINGCHANGE)

    ########################################
    #
    ########################################
    def close(self):
        super().close()
        self._mainwin.quit()

    ########################################
    #
    ########################################
    def set_theme(self, color_scheme):
        self._color_scheme = color_scheme
        is_dark = (color_scheme == PREFERRED_COLOR_SCHEME.DARK) or (color_scheme == PREFERRED_COLOR_SCHEME.AUTO and reg_should_use_dark_mode())
        self._mainwin.apply_theme(is_dark)
        if self.webview_ready:
            self.profile_apply_theme(color_scheme)

    ########################################
    #
    ########################################
    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        style = user32.GetWindowLongA(self._mainwin.hwnd, GWL_STYLE)
        if self._fullscreen:
            if self._mainwin.h_menu:
                user32.SetMenu(self._mainwin.hwnd, None)
            if self._statusbar:
                user32.ShowWindow(self._statusbar.hwnd, SW_HIDE)
            style &= ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
        else:
            style |= (WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
            if self._mainwin.h_menu:
                user32.SetMenu(self._mainwin.hwnd, self._mainwin.h_menu)
            if self._statusbar:
                user32.ShowWindow(self._statusbar.hwnd, SW_SHOW)

        user32.SetWindowLongA(self._mainwin.hwnd, GWL_STYLE, style)
        user32.ShowWindow(self._mainwin.hwnd, SW_SHOWMAXIMIZED if self._fullscreen else SW_NORMAL)

    ########################################
    #
    ########################################
    def escape_fullscreen(self):
        if self._fullscreen:
            self.toggle_fullscreen()

    ########################################
    #
    ########################################
    def run(self):
        self._mainwin.run()

    ########################################
    #
    ########################################
    def check_menu_item(self, idm, flag):
        if self._mainwin.h_menu:
            user32.CheckMenuItem(self._mainwin.h_menu, idm, MF_BYCOMMAND | (MF_CHECKED if flag else MF_UNCHECKED))

    ########################################
    #
    ########################################
    def enable_menu_item(self, idm, flag):
        if self._mainwin.h_menu:
            user32.EnableMenuItem(self._mainwin.h_menu, idm, MF_ENABLED if flag else MF_GRAYED)

    ########################################
    #
    ########################################
    def set_window_title(self, text):
        user32.SetWindowTextW(self._mainwin.hwnd, text)

    ########################################
    #
    ########################################
    def set_status_bar_text(self, text):
        if self._statusbar:
            user32.SetWindowTextW(self._statusbar.hwnd, '  ' + text)

    ########################################
    #
    ########################################
    def show_message_box(self, *args, **kwargs):
        return show_message_box(self.hwnd, *args, **kwargs, is_dark = self._mainwin.is_dark)

    ########################################
    #
    ########################################
    def show_open_file_dialog(self, *args, **kwargs):
        return show_open_file_dialog(self.hwnd, *args, **kwargs)

    ########################################
    #
    ########################################
    def show_save_file_dialog(self, *args, **kwargs):
        return show_save_file_dialog(self.hwnd, *args, **kwargs)
