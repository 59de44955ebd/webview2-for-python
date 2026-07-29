import os
import platform
import sys

APP_NAME = 'WebView2 Demo Winapp'
APP_DIR = os.path.dirname(__file__)
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    # Force local import
    sys.path.append(os.path.realpath(os.path.join(APP_DIR, '..', '..')))

from webview2.winapp.mainwin_themed import *
from webview2.winapp.controls_themed.statusbar import *
from webview2.winapp.dialogs import *
from webview2.embed.winapp import *

from resources import *

if IS_FROZEN:
    HMOD_RESOURCES = kernel32.GetModuleHandleW(None)
else:
    HMOD_RESOURCES = kernel32.LoadLibraryW(os.path.join(APP_DIR, 'resources.dll'))

SETTINGS.ALLOW_HOST_INPUT_PROCESSING = True

# In this demo we use a classic window status bar, so disable webview's inline status bar
SETTINGS.STATUS_BAR_ENABLED = False

# Use a local profile folder
if IS_FROZEN:
    SETTINGS.USER_DATA_FOLDER = os.path.join(APP_DIR, 'profile')

# Allow to use a custom runtime (download .cab and extract e.g. with 7-Zip as local folder 'runtime')
if os.path.isdir(os.path.join(APP_DIR, 'runtime')):
    SETTINGS.BROWSER_EXECUTABLE_FOLDER = os.path.join(APP_DIR, 'runtime')


########################################
#
########################################
class Main(MainWin):

    ########################################
    #
    ########################################
    def __init__(self):

        self.checked_theme_item = IDM_THEME_AUTO
        self.is_fullscreen = False

        self.COMMAND_MESSAGE_MAP = {
            IDM_OPEN:                   self.open_file,
            IDM_SAVE:                   self.save_page,
            IDM_PRINT_TO_PDF:           self.save_as_pdf,
            IDM_SAVE_AS_IMAGE:          self.save_as_image,
            IDM_PRINT:                  self.print,
            IDM_EXIT:                   self.exit,
            IDM_FULLSCREEN:             self.toggle_fullscreen,
            IDM_ESCAPE_FULLSCREEN:      self.escape_fullscreen,
            IDM_THEME_AUTO:             lambda: self.set_theme(IDM_THEME_AUTO),
            IDM_THEME_LIGHT:            lambda: self.set_theme(IDM_THEME_LIGHT),
            IDM_THEME_DARK:             lambda: self.set_theme(IDM_THEME_DARK),
            IDM_ABOUT:                  self.about,
            IDM_DEV_TOOLS:              self.open_dev_tools,
        }

        super().__init__(
            window_title = APP_NAME,
            style = WS_OVERLAPPEDWINDOW | WS_VISIBLE,
            h_accel = user32.LoadAcceleratorsW(HMOD_RESOURCES, LPCWSTR(1)),
            h_icon = user32.LoadIconW(HMOD_RESOURCES, LPCWSTR(1)),
            h_menu = user32.LoadMenuW(HMOD_RESOURCES, LPCWSTR(1)),
        )

        self.webview = WebView2(self, url = 'https://59de44955ebd.github.io/map/')

        self.statusbar = StatusBar(self)

        if reg_should_use_dark_mode():
            self.apply_theme(True)

        ########################################
        #
        ########################################
        def _on_WM_COMMAND(hwnd, wparam, lparam):
            if lparam == 0:
                command_id = LOWORD(wparam)
                if command_id in self.COMMAND_MESSAGE_MAP:
                    self.COMMAND_MESSAGE_MAP[command_id]()

        self.register_message_callback(WM_COMMAND, _on_WM_COMMAND)

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            self.statusbar.update_size()
            if self.statusbar.visible:
                height -= self.statusbar.height
            self.webview.window.set_window_pos(
                width = width,
                height = height,
                flags = SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE
            )

        self.register_message_callback(WM_SIZE, _on_WM_SIZE)

        self.webview.connect(EVENT.STATUS_BAR_TEXT_CHANGED, lambda webview:
                self.statusbar.set_window_text('  ' + webview.get_status_bar_text()))

        ########################################
        #
        ########################################
        def _on_webview_ready(webview):
            webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.AUTO)
            rc = self.get_client_rect()
            width, height = rc.right, rc.bottom - self.statusbar.height
            self.webview.window.set_window_pos(
                width = width,
                height = height,
                flags = SWP_NOMOVE | SWP_NOZORDER | SWP_NOACTIVATE
            )

        self.webview.connect(EVENT.WEBVIEW_READY, _on_webview_ready)

        ########################################
        #
        ########################################
        def _on_WM_SETTINGCHANGE(hwnd, wparam, lparam):
            if self.checked_theme_item != IDM_THEME_AUTO:
                return
            if lparam and cast(lparam, LPCWSTR).value == 'ImmersiveColorSet':
                self.apply_theme(reg_should_use_dark_mode())

        self.register_message_callback(WM_SETTINGCHANGE, _on_WM_SETTINGCHANGE)

        self.webview.set_focus()

    ########################################
    #
    ########################################
    def open_file(self):
        filename = show_open_file_dialog(self.hwnd, title = 'Open File', filter_string = 'HTML Files (*.html; *htm)\0*.html;*.htm\0All Files (*.*)\0*.*\0\0')
        if filename:
            self.webview.load_url(f'file:///{filename}')

    ########################################
    #
    ########################################
    def save_page(self):
        self.webview.show_save_as_ui()

    ########################################
    #
    ########################################
    def save_as_pdf(self):
        filename = show_save_file_dialog(self.hwnd, title = 'Save as PDF', filter_string = 'PDF Files (*.pdf)\0*.pdf\0\0', initial_path = 'page.pdf')
        if filename:
            self.webview.print_to_pdf(filename)

    ########################################
    #
    ########################################
    def save_as_image(self):
        filename = show_save_file_dialog(self.hwnd, title = 'Save as Image', filter_string = 'PNG Files (*.png)\0*.png\0JPEG Files (*.jpg)\0*.jpg\0\0', initial_path = 'page.png')
        if filename:
            image_format = IMAGE_FORMAT.JPEG if filename.lower().endswith('.jpg') else IMAGE_FORMAT.PNG
            istream = POINTER(IStream)()
            hr = shlwapi.SHCreateStreamOnFileW(filename, STGM_CREATE | STGM_WRITE, byref(istream))
            self.webview.capture(image_format, istream)

    ########################################
    #
    ########################################
    def print(self):
        self.webview.show_print_ui()

    ########################################
    #
    ########################################
    def exit(self):
        self.webview.close()
        super().quit()

    ########################################
    #
    ########################################
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.statusbar.show(SW_HIDE if self.is_fullscreen else SW_SHOW)
        style = user32.GetWindowLongA(self.hwnd, GWL_STYLE)
        if self.is_fullscreen:
            user32.SetMenu(self.hwnd, None)
            style &= ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
        else:
            style |= (WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
            user32.SetMenu(self.hwnd, self.h_menu)
        user32.SetWindowLongA(self.hwnd, GWL_STYLE, style)
        self.show(SW_SHOWMAXIMIZED if self.is_fullscreen else SW_SHOWNORMAL)

    ########################################
    #
    ########################################
    def escape_fullscreen(self):
        if self.is_fullscreen:
            self.toggle_fullscreen()

    ########################################
    #
    ########################################
    def about(self):
        show_message_box(
            self.hwnd,
            (
                f'{APP_NAME}\n\nA simple demo based on Python, WinAPI and WebView2.\n\n'
                f'Python version: {sys.version.split()[0]}\n'
                f'Windows version: {platform.platform()}\n'
                f'WebView2 version: {WebView2.environment.get_BrowserVersionString()}'
            ),
            'About'
        )
        self.webview.set_focus()

    ########################################
    #
    ########################################
    def open_dev_tools(self):
        self.webview.open_dev_tools()

    ########################################
    #
    ########################################
    def set_theme(self, idm):
        # Update menu
        user32.CheckMenuItem(self.h_menu, self.checked_theme_item, MF_BYCOMMAND | MF_UNCHECKED)
        self.checked_theme_item = idm
        user32.CheckMenuItem(self.h_menu, self.checked_theme_item, MF_BYCOMMAND | MF_CHECKED)
        # Apply to UI and webview
        is_dark = (idm == IDM_THEME_DARK) or (idm == IDM_THEME_AUTO and reg_should_use_dark_mode())
        self.apply_theme(is_dark)
        self.webview.profile_apply_theme(idm - IDM_THEME_AUTO)


if __name__ == '__main__':
    main = Main()
    main.run()
