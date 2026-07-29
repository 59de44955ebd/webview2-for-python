import os
import platform
import sys

APP_NAME = 'WebView2 Demo Standalone'
APP_DIR = os.path.dirname(__file__)
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    # Force local import
    sys.path.append(os.path.realpath(os.path.join(APP_DIR, '..', '..')))

from webview2.standalone import *

from resources import *

if IS_FROZEN:
    HMOD_RESOURCES = kernel32.GetModuleHandleW(None)
else:
    HMOD_RESOURCES = kernel32.LoadLibraryW(os.path.join(APP_DIR, 'resources.dll'))

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
class Main(WebView2):

    ########################################
    #
    ########################################
    def __init__(self):

        self.checked_theme_item = IDM_THEME_AUTO

        super().__init__(
            window_title = APP_NAME,
            url = 'https://59de44955ebd.github.io/map/',
            h_accel = user32.LoadAcceleratorsW(HMOD_RESOURCES, LPCWSTR(1)),
            h_icon = user32.LoadIconW(HMOD_RESOURCES, LPCWSTR(1)),
            h_menu = user32.LoadMenuW(HMOD_RESOURCES, LPCWSTR(1)),
            statusbar = True,
            color_scheme = PREFERRED_COLOR_SCHEME.AUTO,
        )

        self.set_focus()

    ########################################
    #
    ########################################
    def on_menu(self, webview, idm):

        if idm == IDM_OPEN:
            filename = self.show_open_file_dialog(title = 'Open File', filter_string = 'HTML Files (*.html; *htm)\0*.html;*.htm\0All Files (*.*)\0*.*\0\0')
            if filename:
                self.load_url(f'file:///{filename}')

        elif idm == IDM_SAVE:
            self.show_save_as_ui()

        elif idm == IDM_PRINT:
            self.show_print_ui()

        elif idm == IDM_PRINT_TO_PDF:
            filename = self.show_save_file_dialog(title = 'Save as PDF', filter_string = 'PDF Files (*.pdf)\0*.pdf\0\0', initial_path = 'page.pdf')
            if filename:
                self.print_to_pdf(filename)

        elif idm == IDM_SAVE_AS_IMAGE:
            filename = self.show_save_file_dialog(title = 'Save as Image', filter_string = 'PNG Files (*.png)\0*.png\0JPEG Files (*.jpg)\0*.jpg\0\0', initial_path = 'page.png')
            if filename:
                image_format = IMAGE_FORMAT.JPEG if filename.lower().endswith('.jpg') else IMAGE_FORMAT.PNG
                istream = POINTER(IStream)()
                hr = shlwapi.SHCreateStreamOnFileW(filename, STGM_CREATE | STGM_WRITE, byref(istream))
                self.capture(image_format, istream)

        if idm == IDM_EXIT:
            self.close()

        elif idm == IDM_FULLSCREEN:
            self.toggle_fullscreen()

        elif idm == IDM_ESCAPE_FULLSCREEN:
            self.escape_fullscreen()

        elif idm in (IDM_THEME_AUTO, IDM_THEME_LIGHT, IDM_THEME_DARK):
            self.check_theme_item(idm)

        elif idm == IDM_ABOUT:
            self.show_message_box(
                (
                    f'{APP_NAME}\n\nA simple demo based on Python, WinAPI and WebView2.\n\n'
                    f'Python version: {sys.version.split()[0]}\n'
                    f'Windows version: {platform.platform()}\n'
                    f'WebView2 version: {WebView2.environment.get_BrowserVersionString()}'
                ),
                'About'
            )
            self.set_focus()

        elif idm == IDM_DEV_TOOLS:
            self.open_dev_tools()

    ########################################
    #
    ########################################
    def on_status_bar_text_changed(self, webview):
        self.set_status_bar_text(webview.get_status_bar_text())

    ########################################
    # Reset local profile to PREFERRED_COLOR_SCHEME.AUTO
    ########################################
    def on_webview_ready(self, webview):
        webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.AUTO)

    ########################################
    #
    ########################################
    def check_theme_item(self, idm):
        # Update menu
        self.check_menu_item(self.checked_theme_item, False)
        self.checked_theme_item = idm
        self.check_menu_item(self.checked_theme_item, True)
        # Apply to UI and webview
        super().set_theme(idm - IDM_THEME_AUTO)


if __name__ == '__main__':
    main = Main()
    main.run()
