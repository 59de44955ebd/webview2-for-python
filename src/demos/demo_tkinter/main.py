import json
import os
import sys

import tkinter as tk
from tkinter import messagebox, filedialog

APP_NAME = 'WebView2 Demo Tkinter'
APP_DIR = os.path.dirname(__file__)
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    # Force local import
    sys.path.append(os.path.realpath(os.path.join(APP_DIR, '..', '..')))

from webview2.embed.tkinter import *

# In this demo we use a classic window status bar, so disable webview's inline status bar
SETTINGS.STATUS_BAR_ENABLED = False

if IS_FROZEN:
    SETTINGS.USER_DATA_FOLDER = os.path.join(APP_DIR, 'profile')

if os.path.isdir(os.path.join(APP_DIR, 'runtime')):
    SETTINGS.BROWSER_EXECUTABLE_FOLDER = os.path.join(APP_DIR, 'runtime')


########################################
#
########################################
class Main:

    ########################################
    #
    ########################################
    def __init__(self, root):
        root.withdraw()
        root.iconbitmap(os.path.join(APP_DIR, 'app.ico'))
        root.title(APP_NAME)

        self.theme = tk.IntVar()
        self.theme.set(0)

        menubar = tk.Menu(root)

        # File
        menu = tk.Menu(menubar, tearoff = False)
        menu.add_command(label = "Open File...", accelerator = "Ctrl+O", command = self.open_file, underline = 0)
        root.bind_all("<Control-o>", self.open_file)
        menu.add_separator()
        menu.add_command(label = "Save Page as...", accelerator = "Ctrl+S", command = self.save_page, underline = 0)
        root.bind_all("<Control-s>", self.save_page)
        menu.add_command(label = "Save as PDF...", command = self.save_as_pdf, underline = 10)
        menu.add_command(label = "Save as Image...", command = self.save_as_image, underline = 8)
        menu.add_separator()
        menu.add_command(label = "Print...", accelerator = "Ctrl+P", command=self.show_print_ui, underline = 0)
        root.bind_all("<Control-p>", self.show_print_ui)
        menu.add_separator()
        menu.add_command(label = "Exit", accelerator = "Ctrl+Q", command = self.exit, underline = 0)
        root.bind_all("<Control-q>", self.exit)
        menubar.add_cascade(label = "File", menu = menu, underline = 0)

        # View
        menu = tk.Menu(menubar, tearoff = False)
        menu.add_command(label = "Fullscreen", accelerator = "F11", command = self.toggle_fullscreen, underline = 0)
        root.bind_all("<F11>", self.toggle_fullscreen)
        root.bind_all("<Escape>", self.escape_fullscreen)
        submenu = tk.Menu(menu, tearoff = False)
        menu.add_cascade(label = "Theme", menu=submenu)
        submenu.add_radiobutton(label = "Auto (System)", variable = self.theme, value = PREFERRED_COLOR_SCHEME.AUTO, command = self.set_theme)
        submenu.add_radiobutton(label = "Light", variable = self.theme, value = PREFERRED_COLOR_SCHEME.LIGHT, command = self.set_theme)
        submenu.add_radiobutton(label = "Dark", variable = self.theme, value = PREFERRED_COLOR_SCHEME.DARK, command = self.set_theme)
        menubar.add_cascade(label = "View", menu = menu, underline = 0)

        # Help
        menu = tk.Menu(menubar, tearoff = False)
        menu.add_command(label = "About...", accelerator = "F1", command = self.about, underline = 0)
        root.bind_all("<F1>", self.about)
        menu.add_separator()
        menu.add_command(label = "Open Developer Tools", accelerator = "F12", command = self.open_dev_tools, underline = 0)
        root.bind_all("<F12>", self.open_dev_tools)
        menubar.add_cascade(label = "Help", menu = menu, underline = 0)

        self.webview = WebView2(
            root,
            menubar = menubar,
            statusbar = True,
            url = 'https://59de44955ebd.github.io/map/',
        )

        center_window(root, 1024, 768)
        root.update()

        self.set_theme()

        root.deiconify()

        self.webview.connect(EVENT.STATUS_BAR_TEXT_CHANGED, lambda webview: webview.set_status_bar_text(webview.get_status_bar_text()))

        ########################################
        # Since our app starts with theme = AUTO, always also reset local profile to AUTO.
        ########################################
        def _on_webview_ready(webview):
            webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.AUTO)

        self.webview.connect(EVENT.WEBVIEW_READY, _on_webview_ready)

        ########################################
        #
        ########################################
        def _on_theme_changed():
            if self.theme.get() == PREFERRED_COLOR_SCHEME.AUTO:
                self.set_theme()

        self.webview.expose('theme_changed', _on_theme_changed)

        self.webview.add_script_to_execute_on_document_created("window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => chrome.webview.api.theme_changed());")

        self.webview.set_focus()

    ########################################
    #
    ########################################
    def toggle_fullscreen(self, *args):
        self.webview.toggle_fullscreen()

    ########################################
    #
    ########################################
    def escape_fullscreen(self, *args):
        self.webview.escape_fullscreen()

    ########################################
    #
    ########################################
    def open_file(self, *args):
        res = filedialog.askopenfile(filetypes = [('HTML Files (*.html; *htm)', '*.html;*.htm'), ('All Files (*.*)', '*.*')])
        if res:
            self.webview.load_url(f'file:///{res.name}')

    ########################################
    #
    ########################################
    def save_page(self, *args):
        self.webview.show_save_as_ui()

    ########################################
    #
    ########################################
    def save_as_pdf(self):
        res = filedialog.asksaveasfile(title = 'Save as PDF', filetypes = [('PDF Files', '*.pdf')], initialfile = 'page', defaultextension = '.pdf')
        if res:
            self.webview.print_to_pdf(res.name)

    ########################################
    #
    ########################################
    def save_as_image(self):
        res = filedialog.asksaveasfile(title = 'Save as Image', filetypes = [('PNG Files', '*.png'), ('JPEG Files', '*.jpg')], initialfile = 'page', defaultextension = '.png')
        if res:
            image_format = IMAGE_FORMAT.JPEG if res.name.lower().endswith('.jpg') else IMAGE_FORMAT.PNG
            istream = POINTER(IStream)()
            hr = shlwapi.SHCreateStreamOnFileW(res.name, STGM_CREATE | STGM_WRITE, byref(istream))
            self.webview.capture(image_format, istream)

    ########################################
    #
    ########################################
    def show_print_ui(self, *args):
        self.webview.show_print_ui()

    ########################################
    #
    ########################################
    def exit(self, *args):
        self.webview.close()

    ########################################
    #
    ########################################
    def set_theme(self, *args):
        self.webview.apply_theme(self.theme.get())

    ########################################
    #
    ########################################
    def about(self, *args):
        messagebox.showinfo(
            title = 'About',
            message = (
                f'{APP_NAME}\n\nA simple demo based on Python, Tkinter and WebView2.\n\n'
                f'Python version: {sys.version.split()[0]}\n'
                f'Tkinter version: {tk.TkVersion}\n'
                f'WebView2 version: {WebView2.environment.get_BrowserVersionString()}'
            )
        )
        self.webview.set_focus()

    ########################################
    #
    ########################################
    def open_dev_tools(self, *args):
        self.webview.open_dev_tools()


if __name__ == '__main__':
    root = tk.Tk()
    main = Main(root)
    root.mainloop()
