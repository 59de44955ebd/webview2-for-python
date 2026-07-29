from .. import *
from ..winapp.const import *
from ..winapp.themes import *
from ..winapp.window import *

import System.Windows.Forms as WinForms


########################################
#
########################################
class WebView2(WebView2):

    ########################################
    #
    ########################################
    def __init__(self, *args, **kwargs):

        self.control = WinForms.UserControl()

        super().__init__(parent_hwnd = self.control.Handle.ToInt32(), *args, **kwargs)

        def on_resize(sender, args):
            self.put_bounds(RECT(0, 0, self.control.Width, self.control.Height))

        self.control.Resize += on_resize
