from .. import *
from ..winapp.themes import *


########################################
#
########################################
class WebView2(WebView2):

    ########################################
    #
    ########################################
    def __init__(self, parent_frame, *args, **kwargs):
        super().__init__(parent_hwnd = parent_frame.GetHandle(), *args, **kwargs)
