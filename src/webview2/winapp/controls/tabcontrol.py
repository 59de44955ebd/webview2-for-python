# https://learn.microsoft.com/en-us/windows/win32/controls/tab-control-reference
from ..window import *

class TCITEMW(Structure):
    _fields_ = [
        ("mask", UINT),
        ("dwState", DWORD),
        ("dwStateMask", DWORD),
        ("pszText", LPWSTR),
        ("cchTextMax", INT),
        ("iImage", INT),
        ("lParam", LPARAM),
        ]

class TCHITTESTINFO(Structure):
    _pack_ = 4
    _fields_ = [
        ("pt", POINT),
        ("flags", UINT),
        ]

#typedef struct tagTCKEYDOWN
#{
#    NMHDR hdr;
#    WORD wVKey;
#    UINT flags;
#} NMTCKEYDOWN;

MAX_TAB_TEXT_LEN = MAX_PATH


########################################
# Wrapper Class
########################################
class TabControl(Window):

    ########################################
    #
    ########################################
    def __init__(
        self,
        parent_window = None,
        style = WS_CHILD | WS_VISIBLE,
        ex_style = 0,
        left = 0, top = 0, width = 0, height = 0,
        wrap_hwnd = None,
        h_font = H_FONT_SHELL,

        bg_brush = COLOR_3DFACE + 1,

    ):
        self._bg_brush = bg_brush

        super().__init__(
            WC_TABCONTROL,
            parent_window = parent_window,
            style = style,
            ex_style = ex_style,
            left = left, top = top, width = width, height = height,
            wrap_hwnd = wrap_hwnd,
            h_font = h_font
        )

        self.height = height
        user32.SendMessageW(self.hwnd, WM_CHANGEUISTATE, MAKELONG(UIS_SET, UISF_HIDEFOCUS), 0)

    ########################################
    # custom
    ########################################
    def get_item_text(self, idx):
        buf = create_unicode_buffer(MAX_TAB_TEXT_LEN)
        tc_item = TCITEMW()
        tc_item.mask = TCIF_TEXT
        # If item information is being retrieved, this member specifies the address of the buffer that receives the tab text.
        tc_item.pszText = cast(buf, LPWSTR)
        tc_item.cchTextMax = MAX_TAB_TEXT_LEN
        ok = user32.SendMessageW(self.hwnd, TCM_GETITEMW, idx, byref(tc_item))
        return buf.value

    def get_item_rect(self, idx):
        rc = RECT()
        user32.SendMessageW(self.hwnd, TCM_GETITEMRECT, idx, byref(rc))
        return rc

    def get_cur_sel(self):
        return user32.SendMessageW(self.hwnd, TCM_GETCURSEL, 0, 0)

    def get_item_count(self):
        return user32.SendMessageW(self.hwnd, TCM_GETITEMCOUNT, 0, 0)

#    def find_item_by_data(self, data):
#        cnt = user32.SendMessageW(self.hwnd, TCM_GETITEMCOUNT, 0, 0)
#        tc_item = TCITEMW()
#        tc_item.mask = TCIF_PARAM
#        for iItem in range(cnt):
#            user32.SendMessageW(self.hwnd, TCM_GETITEMW, iItem, byref(tc_item))
#            if tc_item.lParam == data:
#                return iItem

    def get_item(self, idx, mask):
        tc_item = TCITEMW()
        tc_item.mask = mask
        user32.SendMessageW(self.hwnd, TCM_GETITEMW, idx, byref(tc_item))
        return tc_item

    def set_item(self, idx, tc_item):
        return user32.SendMessageW(self.hwnd, TCM_SETITEMW, idx, byref(tc_item))

    def set_item_text(self, idx, text):
        tc_item = TCITEMW()
        tc_item.mask = TCIF_TEXT
        # If item information is being retrieved, this member specifies the address of the buffer that receives the tab text.
        tc_item.pszText = cast(create_unicode_buffer(text), LPWSTR)
        tc_item.cchTextMax = len(text)
        return user32.SendMessageW(self.hwnd, TCM_SETITEMW, idx, byref(tc_item))

#    def get_item_data(self, idx):
#        tc_item = TCITEMW()
#        tc_item.mask = TCIF_PARAM
#        user32.SendMessageW(self.hwnd, TCM_GETITEMW, idx, byref(tc_item))
#        return tc_item.lParam

    def insert_item(self, idx, tc_item):
        user32.SendMessageW(self.hwnd, TCM_INSERTITEMW, idx, byref(tc_item))

    def delete_item(self, idx):
        return user32.SendMessageW(self.hwnd, TCM_DELETEITEM, idx, 0)

    def delete_all_items(self):
        return user32.SendMessageW(self.hwnd, TCM_DELETEALLITEMS, 0, 0)

    def set_cur_sel(self, idx):
        return user32.SendMessageW(self.hwnd, TCM_SETCURSEL, idx, 0)

#    def hit_test(self, hti):
#        return user32.SendMessageW(self.hwnd, TCM_HITTEST, 0, byref(hti))  # TC_HITTESTINFO *

#    def set_item_extra(hwndTC, cb):
#        return user32.SendMessageW((hwndTC), TCM_SETITEMEXTRA, cb, 0)

#    def adjust_rect(self, bLarger, rc):
#        return user32.SendMessageW(self.hwnd, TCM_ADJUSTRECT, bLarger, byref(rc))

#    def set_item_size(self, x, y):
#        return user32.SendMessageW(self.hwnd, TCM_SETITEMSIZE, 0, MAKELPARAM(x,y))

#    def remove_image(self, idx):
#        return user32.SendMessageW(self.hwnd, TCM_REMOVEIMAGE, idx, 0)

#    def set_padding(self,  cx, cy):
#        return user32.SendMessageW(self.hwnd, TCM_SETPADDING, 0, MAKELPARAM(cx, cy))

#    def get_row_count(self):
#        return user32.SendMessageW(self.hwnd, TCM_GETROWCOUNT, 0, 0)

#    def get_tool_tips(self):
#        return user32.SendMessageW(self.hwnd, TCM_GETTOOLTIPS, 0, 0)

#    def set_tool_tips(self, hwndTT):
#        return user32.SendMessageW(self.hwnd, TCM_SETTOOLTIPS, hwndTT, 0)

#    def get_cur_focus(self):
#        return user32.SendMessageW(self.hwnd, TCM_GETCURFOCUS, 0, 0)

#    def set_cur_focus(self, idx):
#        user32.SendMessageW(self.hwnd, TCM_SETCURFOCUS, idx, 0)

#    def set_min_tab_width(self, x):
#        return user32.SendMessageW(self.hwnd, TCM_SETMINTABWIDTH, 0, x)

#    def deselect_all(self, fExcludeFocus):
#        user32.SendMessageW(self.hwnd, TCM_DESELECTALL, fExcludeFocus, 0)

#    def highlight_item(self, idx, fHighlight):
#        return user32.SendMessageW(self.hwnd, TCM_HIGHLIGHTITEM, idx, MAKELONG(fHighlight, 0))

#    def set_extended_style(self, dw):
#        return user32.SendMessageW(self.hwnd, TCM_SETEXTENDEDSTYLE, 0, dw)

#    def get_extended_style(self):
#        return user32.SendMessageW(self.hwnd, TCM_GETEXTENDEDSTYLE, 0, 0)

#    def set_unicode_format(self, fUnicode):
#        return user32.SendMessageW(self.hwnd, TCM_SETUNICODEFORMAT, fUnicode, 0)

#    def get_unicode_format(self) :
#        return user32.SendMessageW(self.hwnd, TCM_GETUNICODEFORMAT, 0, 0)
