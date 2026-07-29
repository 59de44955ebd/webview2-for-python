import os
import sys

import clr
import System

clr.AddReference('System.Windows.Forms')

import System.Windows.Forms as WinForms
from System.Drawing import Color, Icon, Size

APP_NAME = 'WebView2 Demo Windows Forms'
APP_DIR = os.path.realpath(os.path.dirname(__file__))
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    # Force local import
    sys.path.append(os.path.realpath(os.path.join(APP_DIR, '..', '..')))

from webview2.embed.winforms import *

SETTINGS.ALLOW_HOST_INPUT_PROCESSING = True

# In this demo we use a classic window status bar, so disable webview's inline status bar
SETTINGS.STATUS_BAR_ENABLED = False

if IS_FROZEN:
    SETTINGS.USER_DATA_FOLDER = os.path.join(APP_DIR, 'profile')

if os.path.isdir(os.path.join(APP_DIR, 'runtime')):
    SETTINGS.BROWSER_EXECUTABLE_FOLDER = os.path.join(APP_DIR, 'runtime')


class Main(WinForms.Form):

    def __init__(self):

        self._fullscreen = False

        super().__init__()

        self.Text = APP_NAME
        if IS_FROZEN:
            self.Icon = Icon.FromHandle(System.IntPtr(user32.LoadIconW(kernel32.GetModuleHandleW(None), LPCWSTR(1))))
        else:
            self.Icon = Icon(os.path.join(APP_DIR, 'app.ico'))
        self.Size = Size(1024, 768)
        self.StartPosition = WinForms.FormStartPosition.CenterScreen

        self.initialize_component()

        # For subclassing our form to handle dark mode of the menu bar
        self._window = Window(wrap_hwnd = self.Handle.ToInt32())

        if reg_should_use_dark_mode():
            self.apply_theme(True)

        # Menu accelerators don't work in fullscreen mode with hidden menu bar,
        # so lets forward ESC and F11 keydown events from webview to the app.
        def _on_accelerator_key_pressed(webview, args):
            if self._fullscreen and args.get_KeyEventKind() == KEY_EVENT_KIND.KEY_DOWN and args.get_VirtualKey() in (VK_ESCAPE, VK_F11):
                self.on_toggle_fullscreen()

        self.webview.connect(EVENT.ACCELERATOR_KEY_PRESSED, _on_accelerator_key_pressed)

        self.webview.connect(EVENT.STATUS_BAR_TEXT_CHANGED, lambda webview: self._status_label.set_Text(webview.get_status_bar_text()))

        self.webview.set_focus()

    def initialize_component(self):
        self.SuspendLayout()

        # We use an old-fashioned MainMenu instead of MenuStrip because this makes implementing
        # dark mode much easier.
        self._main_menu = WinForms.MainMenu()

        # File
        m = WinForms.MenuItem('&File')
        self._main_menu.MenuItems.Add(m)

        action_item = WinForms.MenuItem('&Open File...')
        action_item.Shortcut = WinForms.Shortcut.CtrlO
        action_item.Click += self.on_open
        m.MenuItems.Add(action_item)

        m.MenuItems.Add(WinForms.MenuItem('-'))

        action_item = WinForms.MenuItem('&Save Page as...')
        action_item.Shortcut = WinForms.Shortcut.CtrlS
        action_item.Click += self.on_save
        m.MenuItems.Add(action_item)

        action_item = WinForms.MenuItem('Save as P&DF...')
        action_item.Click += self.on_save_as_pdf
        m.MenuItems.Add(action_item)

        action_item = WinForms.MenuItem('Save as &Image...')
        action_item.Click += self.on_save_as_image
        m.MenuItems.Add(action_item)

        m.MenuItems.Add(WinForms.MenuItem('-'))

        action_item = WinForms.MenuItem('&Print...')
        action_item.Shortcut = WinForms.Shortcut.CtrlP
        action_item.Click += self.on_print
        m.MenuItems.Add(action_item)

        m.MenuItems.Add(WinForms.MenuItem('-'))

        action_item = WinForms.MenuItem('E&xit')
        action_item.Click += self.on_exit
        m.MenuItems.Add(action_item)

        # View
        m = WinForms.MenuItem('&View')
        self._main_menu.MenuItems.Add(m)

        action_item = WinForms.MenuItem('&Fullscreen')
        action_item.Shortcut = WinForms.Shortcut.F11
        action_item.Click += self.on_toggle_fullscreen
        m.MenuItems.Add(action_item)

        sm = WinForms.MenuItem('&Theme')
        m.MenuItems.Add(sm)

        self._item_theme_auto = WinForms.MenuItem('&Auto (System)')
        self._item_theme_auto.Checked =True
        self._theme = self._item_theme_auto
        self._item_theme_auto.Click += self.on_change_theme
        sm.MenuItems.Add(self._item_theme_auto)

        self._item_theme_light = WinForms.MenuItem('&Light')
        self._item_theme_light.Click += self.on_change_theme
        sm.MenuItems.Add(self._item_theme_light)

        self._item_theme_dark = WinForms.MenuItem('&Dark')
        self._item_theme_dark.Click += self.on_change_theme
        sm.MenuItems.Add(self._item_theme_dark)

        # Help
        m = WinForms.MenuItem('&Help')
        self._main_menu.MenuItems.Add(m)

        action_item = WinForms.MenuItem('&About...')
        action_item.Shortcut = WinForms.Shortcut.F1
        action_item.Click += self.on_about
        m.MenuItems.Add(action_item)

        action_item = WinForms.MenuItem('&Open Developer Tools')
        action_item.Shortcut = WinForms.Shortcut.F12
        action_item.Click += self.on_open_dev_tools
        m.MenuItems.Add(action_item)

        self.Menu = self._main_menu

        self.webview = WebView2(url = "https://59de44955ebd.github.io/map/")
        self.Controls.Add(self.webview.control)
        self.webview.control.Dock = WinForms.DockStyle.Fill

        self._status_strip = WinForms.StatusStrip()
        self.Controls.Add(self._status_strip)
        self._status_label = WinForms.ToolStripStatusLabel()
        self._status_strip.Items.Add(self._status_label)

        self.ResumeLayout(False)
        self.PerformLayout()

    def apply_theme(self, is_dark):
        # Update colors of title bar
        dwm_use_dark_mode(self.Handle.ToInt32(), is_dark)

        # Update colors of menu bar
        theme_menubar(self._window, is_dark)

        # Update colors of menus
        uxtheme.SetPreferredAppMode(PreferredAppMode.ForceDark if is_dark else PreferredAppMode.ForceLight)
        uxtheme.FlushMenuThemes()

        # Update colors of status bar
        if is_dark:
            self._status_strip.BackColor = Color.FromArgb(255, 32, 32, 32)
            self._status_strip.ForeColor = Color.White
        else:
            self._status_strip.BackColor = self._status_strip.DefaultBackColor
            self._status_strip.ForeColor = self._status_strip.DefaultForeColor

        user32.RedrawWindow(self.Handle.ToInt32(), 0, 0, RDW_FRAME | RDW_ERASE | RDW_INVALIDATE)

    def on_open(self, sender, args):
        ofd = WinForms.OpenFileDialog()
        ofd.Filter = "HTML Files|*.html;*.htm|All Files (*.*)|*.*"
        ofd.RestoreDirectory = True
        if ofd.ShowDialog() == WinForms.DialogResult.OK:
            self.webview.load_url(f'file:///{ofd.FileName}')

    def on_save(self, sender, args):
        self.webview.show_save_as_ui()

    def on_save_as_pdf(self, sender, args):
        sfd = WinForms.SaveFileDialog()
        sfd.Filter = "PDF Files|*.pdf"
        sfd.RestoreDirectory = True
        sfd.FileName = 'page.pdf'
        if sfd.ShowDialog() == WinForms.DialogResult.OK:
            self.webview.print_to_pdf(sfd.FileName)

    def on_save_as_image(self, sender, args):
        sfd = WinForms.SaveFileDialog()
        sfd.Filter = "PNG Files|*.png|JPEG Files|*.jpg"
        sfd.RestoreDirectory = True
        sfd.FileName = 'page.png'
        if sfd.ShowDialog() == WinForms.DialogResult.OK:
            filename = sfd.FileName
            image_format = IMAGE_FORMAT.JPEG if filename.lower().endswith('.jpg') else IMAGE_FORMAT.PNG
            istream = POINTER(IStream)()
            hr = shlwapi.SHCreateStreamOnFileW(filename, STGM_CREATE | STGM_WRITE, byref(istream))
            self.webview.capture(image_format, istream)

    def on_print(self, sender, args):
        self.webview.show_print_ui()

    def on_exit(self, sender, args):
        WinForms.Application.Exit()

    def on_toggle_fullscreen(self, *args):
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self.old_style = self.FormBorderStyle
            self.old_state = self.WindowState
            # Hide menu bar and status bar
            self.Menu = None
            self._status_strip.Visible = False
            self.FormBorderStyle = getattr(WinForms.FormBorderStyle, 'None')
            self.WindowState = WinForms.FormWindowState.Maximized
            self.TopMost = True
        else:
            self.TopMost = False
            self.FormBorderStyle = self.old_style
            self.WindowState = self.old_state
            # Show menu bar and status bar
            self.Menu = self._main_menu
            self._status_strip.Visible = True

    def on_change_theme(self, sender, args):
        self._theme.Checked = False
        self._theme = sender
        self._theme.Checked = True

        if self._theme == self._item_theme_auto:
            is_dark = reg_should_use_dark_mode()
            if self.webview.webview_ready:
                self.webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.AUTO)
        else:
            is_dark = self._theme == self._item_theme_dark
            if self.webview.webview_ready:
                self.webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.DARK if is_dark else PREFERRED_COLOR_SCHEME.LIGHT)

        # Apply theme to app UI
        self.apply_theme(is_dark)

    def on_about(self, sender, args):
        WinForms.MessageBox.Show(
            (
                f'{APP_NAME}\n\nA simple demo based on Python, pythonnet, Windows Forms and WebView2.\n\n'
                f'Python version: {sys.version.split()[0]}\n'
                f'pythonnet version: {clr.__version__}\n'
                f'WebView2 version: {WebView2.environment.get_BrowserVersionString()}'
            ),
            'About',
            WinForms.MessageBoxButtons.OK,
            WinForms.MessageBoxIcon.Information
        )

    def on_open_dev_tools(self, sender, args):
        self.webview.open_dev_tools()


if __name__ == '__main__':
    app = Main()
    WinForms.Application.Run(app)
    app.Dispose()
