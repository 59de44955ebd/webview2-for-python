from ctypes import *
from ctypes.wintypes import *

from .const import *
from .types import *

class COLORSCHEME(Structure):
    def __init__(self, *args, **kwargs):
        super(COLORSCHEME, self).__init__(*args, **kwargs)
        self.dwSize = sizeof(self)
    _fields_ = [
        ("dwSize",                DWORD),
        ("clrBtnHighlight",       COLORREF),
        ("clrBtnShadow",          COLORREF),
    ]

class COPYDATASTRUCT(Structure):
    _fields_ = [
        ('dwData', LPARAM),
        ('cbData', DWORD),
        ('lpData', LPVOID)
    ]

class DRAWITEMSTRUCT(Structure):
    _fields_ = [
        ("CtlType", UINT),
        ("CtlID", UINT),
        ("itemID", UINT),
        ("itemAction", UINT),
        ("itemState", UINT),

        ("hwndItem", HWND),
        ("hDC", HDC),
        ("rcItem", RECT),
        ("itemData", ULONG_PTR),
    ]

class LOGFONTW(Structure):
    def __repr__(self):
        return "<LOGFONTW '%s' %d>" % (self.lfFaceName, self.lfHeight)
    _fields_ = [
        ('lfHeight', LONG),
        ('lfWidth', LONG),
        ('lfEscapement', LONG),
        ('lfOrientation', LONG),
        ('lfWeight', LONG),
        ('lfItalic', BYTE),
        ('lfUnderline', BYTE),
        ('lfStrikeOut', BYTE),
        ('lfCharSet', BYTE),
        ('lfOutPrecision', BYTE),
        ('lfClipPrecision', BYTE),
        ('lfQuality', BYTE),
        ('lfPitchAndFamily', BYTE),
        ('lfFaceName', WCHAR * LF_FACESIZE),
    ]

class MEASUREITEMSTRUCT(Structure):
    _fields_ = [
        ("CtlType", UINT),
        ("CtlID", UINT),
        ("itemID", UINT),
        ("itemWidth", UINT),
        ("itemHeight", UINT),
        ("lItemlParam", ULONG_PTR),
    ]

class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT),
        ("ptMaxTrackSize", POINT),
    ]

class NMHDR(Structure):
    _pack_ = 8
    _fields_ = [
        ("hwndFrom", HWND),
        ("idFrom", UINT_PTR),
        ("code", INT),
    ]
#LPNMHDR = POINTER(NMHDR)

class NMCUSTOMDRAW(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("dwDrawStage", DWORD),
        ("hdc", HDC),
        ("rc", RECT),
        ("dwItemSpec", DWORD_PTR),
        ("uItemState", UINT),
        ("lItemlParam", LPARAM),
    ]
#LPNMCUSTOMDRAW = POINTER(NMCUSTOMDRAW)

class NMMOUSE(Structure):
    _fields_ = [
        ("hdr", NMHDR),
        ("dwItemSpec", DWORD_PTR),
        ("dwItemData", DWORD_PTR),
        ("pt", POINT),
        ("dwHitInfo", LPARAM),
    ]

class PAINTSTRUCT(Structure):
    _fields_ = [
        ("hdc",            HDC),
        ("fErase",         BOOL),
        ("rcPaint",        RECT),
        ("fRestore",       BOOL),
        ("fIncUpdate",     BOOL),
        ("rgbReserved",    BYTE * 32),
    ]

class SHFILEINFOW(Structure):
    _fields_ = [
        ("hIcon",         HICON),
        ("iIcon",         INT),
        ("dwAttributes",  DWORD),
        ("szDisplayName", WCHAR * MAX_PATH),
        ("szTypeName",    WCHAR * 80),
    ]

class TEXTMETRICW(Structure):
    _fields_ = [
        ("tmHeight", 			    LONG),
        ("tmAscent",                LONG),
        ("tmDescent",               LONG),
        ("tmInternalLeading",       LONG),
        ("tmExternalLeading",       LONG),
        ("tmAveCharWidth",          LONG),
        ("tmMaxCharWidth",          LONG),
        ("tmWeight",                LONG),
        ("tmOverhang",              LONG),
        ("tmDigitizedAspectX",      LONG),
        ("tmDigitizedAspectY",      LONG),
        ("tmFirstChar",             WCHAR),
        ("tmLastChar",              WCHAR),
        ("tmDefaultChar",           WCHAR),
        ("tmBreakChar",             WCHAR),
        ("tmItalic",                BYTE),
        ("tmUnderlined",            BYTE),
        ("tmStruckOut",             BYTE),
        ("tmPitchAndFamily",        BYTE),
        ("tmCharSet",               BYTE),
    ]

class TRACKMOUSEEVENT(Structure):
    def __init__(self, *args, **kwargs):
        super(TRACKMOUSEEVENT, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", DWORD),
        ("dwFlags", DWORD),
        ("hwndTrack", HWND),
        ("dwHoverTime", DWORD),
    ]

class WNDCLASSEXW(Structure):
    def __init__(self, *args, **kwargs):
        super(WNDCLASSEXW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", c_uint),
        ("style", c_uint),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", c_int),
        ("cbWndExtra", c_int),
        ("hInstance", HANDLE),
        ("hIcon", HANDLE),
        ("hCursor", HANDLE),
        ("hbrBackground", HANDLE),
        ("lpszMenuName", LPCWSTR),
        ("lpszClassName", LPCWSTR),
        ("hIconSm", HANDLE)
    ]

class SHSTOCKICONINFO(Structure):
    def __init__(self, *args, **kwargs):
        super(SHSTOCKICONINFO, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = (
        ('cbSize', DWORD),
        ('hIcon', HANDLE),
        ('iSysImageIndex', INT),
        ('iIcon', INT),
        ('szPath', WCHAR * MAX_PATH),
    )

class CWPRETSTRUCT(Structure):
    _fields_ = [
        ("lResult", LPARAM),
        ("lParam", LPARAM),
        ("wParam", WPARAM),
        ("message", UINT),
        ("hwnd", HWND),
    ]
