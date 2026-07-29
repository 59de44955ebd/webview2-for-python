import json
import os
import sys

import wx

APP_NAME = 'WebView Demo wxPython'
APP_DIR = os.path.realpath(os.path.dirname(__file__))
IS_FROZEN = getattr(sys, 'frozen', False)

if not IS_FROZEN:
    # Force local import
    sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from webview2.embed.wxpython import *

SETTINGS.ALLOW_HOST_INPUT_PROCESSING = True

wx.ID_SAVE_PDF = 100
wx.ID_SAVE_IMAGE = 101
wx.ID_OPEN_DEV_TOOLS = 102
wx.ID_ESCAPE_FULLSCREEN = 103

# In this demo we use a classic window status bar, so disable webview's inline status bar
SETTINGS.STATUS_BAR_ENABLED = False

if IS_FROZEN:
    SETTINGS.USER_DATA_FOLDER = os.path.join(APP_DIR, 'profile')

if os.path.isdir(os.path.join(APP_DIR, 'runtime')):
    SETTINGS.BROWSER_EXECUTABLE_FOLDER = os.path.join(APP_DIR, 'runtime')


class Main(wx.Frame):

    def __init__(self):
        super().__init__(None, -1, title = APP_NAME, size = (1024, 768))

        self.SetIcon(wx.Icon(os.path.join(APP_DIR, 'app.ico')))

        menuBar = wx.MenuBar()

        menu = wx.Menu()
        menuBar.Append(menu, '&File')

        menu.Append(wx.ID_OPEN, '&Open File...\tCtrl+O')
        menu.AppendSeparator()
        menu.Append(wx.ID_SAVE, '&Save Page as...\tCtrl+S')
        menu.Append(wx.ID_SAVE_PDF, 'Save as P&DF...')
        menu.Append(wx.ID_SAVE_IMAGE, 'Save as &Image...')
        menu.AppendSeparator()
        menu.Append(wx.ID_PRINT, '&Print...')
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, 'Exit\tCtrl+Q', 'Exit')

        menu = wx.Menu()
        menuBar.Append(menu, '&View')
        menu.Append(wx.ID_MAXIMIZE_FRAME, '&Fullscreen\tF11', 'Fullscreen')

        menu = wx.Menu()
        menuBar.Append(menu, '&Help')

        menu.Append(wx.ID_ABOUT, '&About...\tF1', 'About')
        menu.Append(wx.ID_OPEN_DEV_TOOLS, '&Open Developer Tools\tF12', 'Open Developer Tools')

        self.SetMenuBar(menuBar)

        # Accelerator without menu item
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_ESCAPE_FULLSCREEN)])
        self.SetAcceleratorTable(accel_tbl)

        self.Bind(wx.EVT_MENU, self.OnMenu)

        self.statusbar = wx.StatusBar(self)
        self.SetStatusBar(self.statusbar)

        self.webview = WebView2(self, url = 'https://59de44955ebd.github.io/map/')

        self._fullscreen = False

        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Centre()
        self.Show()

        self.webview.connect(EVENT.STATUS_BAR_TEXT_CHANGED, lambda webview: self.statusbar.SetStatusText(webview.get_status_bar_text()))

        ########################################
        # Since our app starts with theme = AUTO, always also reset local profile to AUTO.
        ########################################
        def _on_webview_ready(webview):
            webview.profile_apply_theme(PREFERRED_COLOR_SCHEME.AUTO)

        self.webview.connect(EVENT.WEBVIEW_READY, _on_webview_ready)

        self.webview.expose('theme_changed', self.apply_theme)

        self.webview.add_script_to_execute_on_document_created("window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', ({matches}) => chrome.webview.api.theme_changed(matches));")

        self.webview.set_focus()

    ########################################
    #
    ########################################
    def OnMenu(self, evt):

        if evt.Id == wx.ID_OPEN:
            with wx.FileDialog(self, 'Open File', wildcard = 'HTML Files|*.html;*htm|All Files|*.*', style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                filename = fileDialog.GetPath()
            self.webview.load_url(f'file:///{filename}')

        elif evt.Id == wx.ID_SAVE:
            self.webview.show_save_as_ui()

        elif evt.Id == wx.ID_SAVE_PDF:
            with wx.FileDialog(self, 'Save as PDF', wildcard = 'PDF Files|*.pdf', style = wx.FD_SAVE) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                filename = fileDialog.GetPath()
            self.webview.print_to_pdf(filename)

        elif evt.Id == wx.ID_PRINT:
             self.webview.show_print_ui()

        elif evt.Id == wx.ID_SAVE_IMAGE:
            with wx.FileDialog(self, 'Save as Image', wildcard = 'PNG Files|*.png|JPEG Files|*.jpg', style = wx.FD_SAVE) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                filename = fileDialog.GetPath()
            image_format = IMAGE_FORMAT.JPEG if filename.lower().endswith('.jpg') else IMAGE_FORMAT.PNG
            istream = POINTER(IStream)()
            hr = shlwapi.SHCreateStreamOnFileW(filename, STGM_CREATE | STGM_WRITE, byref(istream))
            self.webview.capture(image_format, istream)

        elif evt.Id == wx.ID_EXIT:
            self.Close()

        elif evt.Id == wx.ID_MAXIMIZE_FRAME:
            self.toggle_fullscreen()

        elif evt.Id == wx.ID_ESCAPE_FULLSCREEN:
            if self._fullscreen:
                self.toggle_fullscreen()

        elif evt.Id == wx.ID_ABOUT:
            self.about()

        elif evt.Id == wx.ID_OPEN_DEV_TOOLS:
            self.webview.open_dev_tools()

    ########################################
    #
    ########################################
    def OnSize(self, evt):
        self.webview.put_bounds(RECT(0, 0, self.ClientRect.width, self.ClientRect.height))

    ########################################
    #
    ########################################
    def apply_theme(self, is_dark):

        # Update window titlebar
        dwm_use_dark_mode(self.GetHandle(), is_dark)

        # (My) wxPython has issues with live updating the theme of the statusbar,
        # so let's replace it with a new one.
        text = self.statusbar.GetStatusText()
        self.statusbar.Destroy()
        self.statusbar = wx.StatusBar(self)
        self.SetStatusBar(self.statusbar)
        if text:
            self.statusbar.SetStatusText(text)

    ########################################
    #
    ########################################
    def toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.ShowFullScreen(self._fullscreen)
        self.webview.set_focus()

    ########################################
    #
    ########################################
    def about(self):
        dlg = wx.MessageDialog(
            self,
            (
                f'{APP_NAME}\n\nA simple demo based on Python, wxPython and WebView2.\n\n'
                f'Python version: {sys.version.split()[0]}\n'
                f'wxPython version: {wx.__version__}\n'
                f'WebView2 version: {WebView2.environment.get_BrowserVersionString()}'
            ),
            'About',
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()
        self.webview.set_focus()


if __name__ == '__main__':
    app = wx.App()
    app.SetAppearance(app.Appearance.System)
    main = Main()
    app.MainLoop()
